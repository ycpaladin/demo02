import json
from datetime import datetime
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from metadata.models import List, ListView
from data.query_builder import QueryBuilder
from data.serializer_factory import SerializerFactory


class DynamicRecordView(APIView):

    def _get_list(self, app_id, list_url):
        from django.db.models import Q
        return List.objects.get(
            Q(application_id=app_id),
            Q(url=list_url) | Q(url='/' + list_url),
            is_deleted=False,
        )

    def get(self, request, app_id, list_url):
        lst = self._get_list(app_id, list_url)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        sort = request.query_params.get('sort', '')
        order = request.query_params.get('order', 'asc')
        filter_str = request.query_params.get('filter', '')

        view_key = request.query_params.get('view')
        if view_key:
            view_obj = ListView.objects.filter(list=lst, url_key=view_key).first()
            if view_obj:
                view_config = view_obj.config or {}
                if not sort and view_config.get('default_sort'):
                    sort = view_config['default_sort']
                if not filter_str and view_config.get('default_filter'):
                    filter_str = view_config['default_filter']
                if view_config.get('page_size'):
                    page_size = view_config['page_size']

        result = QueryBuilder.execute_query(lst.table_name, filter_str, sort, order, page, page_size)
        for row in result['results']:
            row['data'] = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat()
            if row.get('updated_at'):
                row['updated_at'] = row['updated_at'].isoformat()
        return Response(result)

    def post(self, request, app_id, list_url):
        lst = self._get_list(app_id, list_url)
        SerializerClass = SerializerFactory.create_serializer(lst)
        serializer = SerializerClass(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(instance, status=status.HTTP_201_CREATED)


class DynamicRecordDetailView(APIView):
    def _get_list(self, app_id, list_url):
        from django.db.models import Q
        return List.objects.get(
            Q(application_id=app_id),
            Q(url=list_url) | Q(url='/' + list_url),
            is_deleted=False,
        )

    def _get_record(self, table_name, record_id):
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id, data, created_at, updated_at FROM [{table_name}] WHERE id = %s",
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

    def get(self, request, app_id, list_url, record_id):
        lst = self._get_list(app_id, list_url)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        return Response(record)

    def put(self, request, app_id, list_url, record_id):
        lst = self._get_list(app_id, list_url)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        SerializerClass = SerializerFactory.create_serializer(lst)
        serializer = SerializerClass(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.update(record, serializer.validated_data)
        return Response(updated)

    def delete(self, request, app_id, list_url, record_id):
        lst = self._get_list(app_id, list_url)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        data = record['data'] or {}
        data['_is_deleted'] = True
        data['_deleted_at'] = datetime.now().isoformat()
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE [{lst.table_name}] SET data = %s, updated_at = GETDATE() WHERE id = %s",
                [json.dumps(data, ensure_ascii=False, default=str), record_id]
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DynamicRecordBatchView(APIView):
    def patch(self, request, app_id, list_url):
        lst = List.objects.get(application_id=app_id, url=list_url, is_deleted=False)
        record_ids = request.data.get('ids', [])
        field_key = request.data.get('field')
        value = request.data.get('value')

        if not record_ids or not field_key:
            return Response({'detail': 'ids and field are required'}, status=400)

        with connection.cursor() as cursor:
            for rid in record_ids:
                cursor.execute(f"SELECT data FROM [{lst.table_name}] WHERE id = %s", [rid])
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    data[field_key] = value
                    cursor.execute(
                        f"UPDATE [{lst.table_name}] SET data = %s, updated_at = GETDATE() WHERE id = %s",
                        [json.dumps(data, ensure_ascii=False, default=str), rid]
                    )
        return Response({'updated': len(record_ids)})
