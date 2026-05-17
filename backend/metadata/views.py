import uuid
from datetime import datetime
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from metadata.models import ContentType, ContentTypeField, List
from metadata.serializers import (
    ContentTypeSerializer, ContentTypeFieldSerializer,
    ListSerializer,
)


class ContentTypeViewSet(viewsets.ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer


class ContentTypeFieldViewSet(viewsets.ModelViewSet):
    serializer_class = ContentTypeFieldSerializer

    def get_queryset(self):
        return ContentTypeField.objects.filter(content_type_id=self.kwargs['ct_id']).order_by('order')

    def perform_create(self, serializer):
        last = ContentTypeField.objects.filter(content_type_id=self.kwargs['ct_id']).order_by('-order').first()
        next_order = (last.order + 1) if last else 0
        serializer.save(content_type_id=self.kwargs['ct_id'], order=next_order)

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request, ct_id=None):
        """Reorder fields — body: { ordered_ids: [...] }"""
        ordered_ids = request.data.get('ordered_ids', [])
        for i, fid in enumerate(ordered_ids):
            ContentTypeField.objects.filter(id=fid, content_type_id=ct_id).update(order=i)
        return Response({'status': 'ok'})


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer

    def get_queryset(self):
        return List.objects.filter(application_id=self.kwargs['app_id'], is_deleted=False)

    def perform_create(self, serializer):
        app_id = self.kwargs['app_id']
        instance = serializer.save(
            application_id=app_id,
            table_name=f"dyn_{serializer.validated_data['key']}",
        )
        # Use raw SQL to create the dynamic table
        from django.db import connection
        table_name = instance.table_name
        sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            data JSONB NOT NULL,
            is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            cursor.execute(f'CREATE INDEX IF NOT EXISTS "idx_{table_name}_is_deleted" ON "{table_name}" (is_deleted) WHERE is_deleted = FALSE')

            # 为内容类型的继承字段创建索引
            if instance.content_type:
                from metadata.managers import ContentTypeManager
                inherited = ContentTypeManager.resolve_fields(instance.content_type)
                for f in inherited:
                    ft = f.get('field_type__key', 'text') or 'text'
                    self._create_field_index(cursor, table_name, f['key'], ft)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])

    @action(detail=True, methods=['get'])
    def form_schema(self, request, app_id=None, pk=None):
        lst = self.get_object()
        fields = lst.get_all_fields()
        from core.models import FieldValidator
        validators = {v.key: v for v in FieldValidator.objects.all()}
        from core.validation import ValidationEngine

        schema = {'list_id': str(lst.id), 'list_name': lst.name, 'fields': []}
        for f in fields:
            field_data = {
                'key': f['key'],
                'name': f['name'],
                'field_type': f['field_type__key'],
                'required': f['required'],
                'unique': f['unique'],
                'searchable': f.get('searchable', False),
                'search_type': f.get('search_type', ''),
                'config': f['config'],
                'rules': ValidationEngine.build_frontend_rules(f, validators),
            }
            if f['field_type__key'] in ('select', 'multi_select'):
                field_data['options'] = f['config'].get('options', [])
            schema['fields'].append(field_data)
        return Response(schema)


    @action(detail=True, methods=['get', 'put'], url_path='schema')
    def schema_view(self, request, app_id=None, pk=None):
        """GET: 返回完整 schema（字段合并继承），PUT: 整体保存"""
        lst = self.get_object()

        if request.method == 'GET':
            # 合并继承字段 + 扩展字段
            all_fields = lst.get_all_fields()
            ext_fields = lst.get_extension_fields()
            ext_keys = {f['key'] for f in ext_fields}

            fields_out = []
            for f in all_fields:
                item = {
                    'key': f['key'],
                    'name': f['name'],
                    'field_type': f['field_type__key'],
                    'required': f['required'],
                    'unique': f['unique'],
                    'searchable': f.get('searchable', False),
                    'search_type': f.get('search_type', ''),
                    'order': f.get('order', 0),
                    'config': f['config'],
                    'validators': f['validators'],
                    'is_extension': f['key'] in ext_keys,
                }
                # 扩展字段包含 id
                if item['is_extension']:
                    ext = next((e for e in ext_fields if e['key'] == f['key']), None)
                    if ext:
                        item['id'] = ext.get('id')
                fields_out.append(item)

            return Response({
                'fields': fields_out,
                'views': lst.get_views(),
                'form': lst.schema.get('form', {}),
            })

        # PUT — 整体保存
        data = request.data
        if not isinstance(data, dict):
            return Response({'error': 'body must be a JSON object'}, status=status.HTTP_400_BAD_REQUEST)

        # 记录旧字段，用于 diff 索引
        old_keys = {f['key'] for f in lst.get_extension_fields()}

        # 保存扩展字段（分配 id 给新增字段）
        ext_fields = data.get('fields', [])
        ext_fields = self._validate_extension_fields(lst, ext_fields)
        self._assign_ids(ext_fields)
        lst.set_extension_fields(ext_fields)

        # 保存视图：分配 id 给新增视图，校验默认视图唯一性
        views = data.get('views', [])
        self._validate_views(views)
        self._assign_ids(views)

        # 保存表单布局
        form = data.get('form', {})

        lst.schema = {
            'fields': ext_fields,
            'views': views,
            'form': form,
        }
        lst.save(update_fields=['schema', 'updated_at'])

        # 维护字段索引：新增的建索引，删除的删索引
        new_keys = {f['key'] for f in ext_fields}
        added = new_keys - old_keys
        removed = old_keys - new_keys
        self._sync_field_indexes(lst.table_name, added, removed, ext_fields)

        return Response({'status': 'ok', 'schema': lst.schema})

    def _validate_extension_fields(self, lst, fields):
        """校验扩展字段 key 不重复，并自动过滤掉继承字段"""
        inherited_keys = set()
        if lst.content_type:
            from metadata.managers import ContentTypeManager
            for f in ContentTypeManager.resolve_fields(lst.content_type):
                inherited_keys.add(f['key'])
        # 自动过滤继承字段（前端可能误传），只保留扩展字段
        ext_fields = [f for f in fields if f['key'] not in inherited_keys]
        keys = [f['key'] for f in ext_fields]
        if len(keys) != len(set(keys)):
            raise serializers.ValidationError({'fields': '扩展字段 key 重复'})
        return ext_fields

    def _assign_ids(self, items):
        """给没有 id 的条目分配 UUID"""
        for item in items:
            if not item.get('id'):
                item['id'] = str(uuid.uuid4())

    def _sync_field_indexes(self, table_name, added_keys, removed_keys, ext_fields):
        """自动维护字段索引：新增字段建 GIN 索引，删除字段删索引"""
        from django.db import connection

        # 构建 key → field_type 映射
        type_map = {f['key']: f.get('field_type', 'text') for f in ext_fields}

        with connection.cursor() as c:
            for key in added_keys:
                ft = type_map.get(key, 'text')
                self._create_field_index(c, table_name, key, ft)
            for key in removed_keys:
                self._drop_field_indexes(c, table_name, key)

    @staticmethod
    def _create_field_index(cursor, table_name, key, field_type):
        # 文本类字段用 trigram GIN，其他用 btree
        idx_name = f'idx_{table_name}_f_{key}'
        if field_type in ('text', 'long_text'):
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table_name}" '
                f"USING GIN ((data->>'{key}') gin_trgm_ops)"
            )
        else:
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table_name}" '
                f"((data->>'{key}'))"
            )

    @staticmethod
    def _drop_field_indexes(cursor, table_name, key):
        # trigram GIN
        cursor.execute(f'DROP INDEX IF EXISTS "idx_{table_name}_f_{key}"')
        # btree 备用名
        cursor.execute(f'DROP INDEX IF EXISTS "idx_{table_name}_f_{key}_btree"')

    def _validate_views(self, views):
        """校验视图：默认视图有且仅有一个，url_key 唯一"""
        if not views:
            raise serializers.ValidationError({'views': '至少需要一个视图'})
        defaults = [v for v in views if v.get('is_default')]
        if len(defaults) != 1:
            raise serializers.ValidationError({'views': '必须有且仅有一个默认视图'})
        url_keys = [v.get('url_key', '') for v in views]
        if len(url_keys) != len(set(url_keys)):
            raise serializers.ValidationError({'views': '视图 url_key 重复'})
        for v in views:
            if not v.get('url_key'):
                v['url_key'] = f"view_{v.get('id', '')[:8]}"
