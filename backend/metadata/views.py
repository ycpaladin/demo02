from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from metadata.models import ContentType, ContentTypeField, List, ListField, ListView
from metadata.serializers import (
    ContentTypeSerializer, ContentTypeFieldSerializer,
    ListSerializer, ListFieldSerializer, ListViewSerializer,
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
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)

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


class ListFieldViewSet(viewsets.ModelViewSet):
    serializer_class = ListFieldSerializer

    def get_queryset(self):
        return ListField.objects.filter(list_id=self.kwargs['list_id']).order_by('order')

    def perform_create(self, serializer):
        # auto-increment order
        last = ListField.objects.filter(list_id=self.kwargs['list_id']).order_by('-order').first()
        next_order = (last.order + 1) if last else 0
        serializer.save(list_id=self.kwargs['list_id'], order=next_order)

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request, list_id=None):
        """Reorder fields — body: { ordered_ids: [...] }"""
        ordered_ids = request.data.get('ordered_ids', [])
        for i, fid in enumerate(ordered_ids):
            ListField.objects.filter(id=fid, list_id=list_id).update(order=i)
        return Response({'status': 'ok'})


class ListViewViewSet(viewsets.ModelViewSet):
    serializer_class = ListViewSerializer

    def get_queryset(self):
        return ListView.objects.filter(list_id=self.kwargs['list_id'])

    def perform_create(self, serializer):
        serializer.save(list_id=self.kwargs['list_id'])
