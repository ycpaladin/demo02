import json
from datetime import datetime
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from metadata.models import List
from data.query_builder import QueryBuilder
from data.serializer_factory import SerializerFactory


class DynamicRecordView(APIView):

    def _get_list(self, app_id, list_id):
        return List.objects.get(id=list_id, application_id=app_id, is_deleted=False)

    def get(self, request, app_id, list_id):
        lst = self._get_list(app_id, list_id)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        sort = request.query_params.get('sort', '')
        order = request.query_params.get('order', 'asc')
        filter_str = request.query_params.get('filter', '')
        where_json = None

        view_key = request.query_params.get('view')
        if view_key:
            view_config = lst.get_view_by_key(view_key) or {}
            if view_config:
                if not sort:
                    order_by = view_config.get('orderBy', [])
                    if order_by:
                        sort_parts = []
                        for ob in order_by:
                            sort_parts.append(f"{ob['field']}:{ob['sort'].lower()}")
                        sort = ','.join(sort_parts)
                if 'where' in view_config and not filter_str:
                    where_json = view_config['where']
                if view_config.get('default_page_size'):
                    page_size = view_config['default_page_size']

        # 查询参数的 where 优先级高于视图
        where_param = request.query_params.get('where')
        if where_param:
            where_json = json.loads(where_param)

        result = QueryBuilder.execute_query(
            lst.table_name, filter_str, sort, order, page, page_size, where_json,
        )
        for row in result['results']:
            row['data'] = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat()
            if row.get('updated_at'):
                row['updated_at'] = row['updated_at'].isoformat()
        return Response(result)

    def post(self, request, app_id, list_id):
        lst = self._get_list(app_id, list_id)
        SerializerClass = SerializerFactory.create_serializer(lst)
        serializer = SerializerClass(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(instance, status=status.HTTP_201_CREATED)


class DynamicRecordDetailView(APIView):
    def _get_list(self, app_id, list_id):
        return List.objects.get(id=list_id, application_id=app_id, is_deleted=False)

    def _get_record(self, table_name, record_id):
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT id, data, created_at, updated_at FROM "{table_name}" WHERE id = %s',
                [record_id]
            )
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if not row:
                return None
            record = dict(zip(columns, row))
            record['data'] = json.loads(record['data']) if isinstance(record['data'], str) else record['data']
            if record.get('created_at'):
                record['created_at'] = record['created_at'].isoformat()
            if record.get('updated_at'):
                record['updated_at'] = record['updated_at'].isoformat()
            return record

    def get(self, request, app_id, list_id, record_id):
        lst = self._get_list(app_id, list_id)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        return Response(record)

    def put(self, request, app_id, list_id, record_id):
        lst = self._get_list(app_id, list_id)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        SerializerClass = SerializerFactory.create_serializer(lst)
        serializer = SerializerClass(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.update(record, serializer.validated_data)
        return Response(updated)

    def delete(self, request, app_id, list_id, record_id):
        lst = self._get_list(app_id, list_id)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        data = record['data'] or {}
        data['_deleted_at'] = datetime.now().isoformat()
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE "{lst.table_name}" SET data = %s, is_deleted = TRUE, updated_at = NOW() WHERE id = %s',
                [json.dumps(data, ensure_ascii=False, default=str), record_id]
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DynamicRecordBatchView(APIView):
    def patch(self, request, app_id, list_id):
        lst = List.objects.get(application_id=app_id, id=list_id, is_deleted=False)
        record_ids = request.data.get('ids', [])
        field_key = request.data.get('field')
        value = request.data.get('value')

        if not record_ids or not field_key:
            return Response({'detail': 'ids and field are required'}, status=400)

        with connection.cursor() as cursor:
            for rid in record_ids:
                cursor.execute(f'SELECT data FROM "{lst.table_name}" WHERE id = %s', [rid])
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    data[field_key] = value
                    cursor.execute(
                        f'UPDATE "{lst.table_name}" SET data = %s, updated_at = NOW() WHERE id = %s',
                        [json.dumps(data, ensure_ascii=False, default=str), rid]
                    )
        return Response({'updated': len(record_ids)})
