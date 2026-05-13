import json
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from metadata.models import List
from data.table_builder import DynamicTableBuilder


class TrashView(APIView):
    def get(self, request, app_id):
        deleted_lists = List.objects.filter(application_id=app_id, is_deleted=True)
        deleted_records = []

        for lst in List.objects.filter(application_id=app_id, is_deleted=False):
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"SELECT id, data, updated_at FROM [{lst.table_name}] WHERE JSON_VALUE(data, '$._is_deleted') = 'true'"
                    )
                    columns = [col[0] for col in cursor.description]
                    for row in cursor.fetchall():
                        rec = dict(zip(columns, row))
                        rec['data'] = json.loads(rec['data']) if isinstance(rec['data'], str) else rec['data']
                        if rec.get('updated_at'):
                            rec['updated_at'] = rec['updated_at'].isoformat()
                        rec['_list_name'] = lst.name
                        rec['_list_id'] = str(lst.id)
                        rec['_list_url'] = lst.url
                        rec['_type'] = 'record'
                        deleted_records.append(rec)
                except Exception:
                    pass

        trash_items = []
        for lst in deleted_lists:
            trash_items.append({
                'id': str(lst.id),
                'type': 'list',
                'name': lst.name,
                'deleted_at': lst.deleted_at.isoformat() if lst.deleted_at else None,
            })
        for rec in deleted_records:
            trash_items.append({
                'id': rec['id'],
                'type': 'record',
                'name': f'{rec["_list_name"]} / {str(rec["data"])[:50]}',
                'list_id': rec['_list_id'],
                'list_url': rec['_list_url'],
                'deleted_at': rec.get('updated_at'),
            })

        trash_items.sort(key=lambda x: x.get('deleted_at') or '', reverse=True)
        return Response(trash_items)

    def post(self, request, app_id, item_id):
        item_type = request.data.get('type')
        if item_type == 'list':
            lst = List.objects.get(id=item_id, application_id=app_id, is_deleted=True)
            lst.is_deleted = False
            lst.deleted_at = None
            lst.save(update_fields=['is_deleted', 'deleted_at'])
            return Response({'status': 'restored'})

        elif item_type == 'record':
            list_id = request.data.get('list_id')
            lst = List.objects.get(id=list_id, application_id=app_id)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT data FROM [{lst.table_name}] WHERE id = %s", [item_id])
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    data['_is_deleted'] = False
                    data['_deleted_at'] = None
                    cursor.execute(
                        f"UPDATE [{lst.table_name}] SET data = %s, updated_at = GETDATE() WHERE id = %s",
                        [json.dumps(data, ensure_ascii=False, default=str), item_id]
                    )
            return Response({'status': 'restored'})

        return Response({'detail': 'Invalid type'}, status=400)

    def delete(self, request, app_id, item_id):
        item_type = request.query_params.get('type')
        if item_type == 'list':
            lst = List.objects.get(id=item_id, application_id=app_id, is_deleted=True)
            DynamicTableBuilder.drop_table(lst.table_name)
            lst.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        elif item_type == 'record':
            list_id = request.query_params.get('list_id')
            lst = List.objects.get(id=list_id, application_id=app_id)
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM [{lst.table_name}] WHERE id = %s", [item_id])
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Invalid type'}, status=400)
