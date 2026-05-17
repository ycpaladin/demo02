import json
from rest_framework import serializers
from core.models import FieldValidator
from core.validation import ValidationEngine


class SerializerFactory:
    @classmethod
    def create_serializer(cls, list_obj):
        fields_def = list_obj.get_all_fields()
        validators_map = {v.key: v for v in FieldValidator.objects.all()}

        serializer_fields = {}
        unique_fields = []

        for f in fields_def:
            field_key = f['key']
            drf_field = ValidationEngine.build_field(f, validators_map)
            serializer_fields[field_key] = drf_field
            if f.get('unique'):
                unique_fields.append(field_key)

        Meta = type('Meta', (), {'ref_name': f'DynamicSerializer_{list_obj.key}'})

        def create(self, validated_data):
            from django.db import connection
            import uuid
            record_id = str(uuid.uuid4())
            data = {**validated_data, '_is_deleted': False, '_deleted_at': None}
            with connection.cursor() as cursor:
                cursor.execute(
                    f'INSERT INTO "{list_obj.table_name}" (id, data) VALUES (%s, %s)',
                    [record_id, json.dumps(data, ensure_ascii=False, default=str)]
                )
            data['id'] = record_id
            return data

        def update(self, instance, validated_data):
            from django.db import connection
            existing_data = instance.get('data', instance) if isinstance(instance, dict) else {}
            if isinstance(existing_data, str):
                existing_data = json.loads(existing_data)
            merged = {**existing_data, **validated_data}
            with connection.cursor() as cursor:
                cursor.execute(
                    f'UPDATE "{list_obj.table_name}" SET data = %s, updated_at = NOW() WHERE id = %s',
                    [json.dumps(merged, ensure_ascii=False, default=str), instance['id']]
                )
            merged['id'] = instance['id']
            return merged

        def validate(self, data):
            from django.db import connection
            for fk in unique_fields:
                if fk in data:
                    value = data[fk]
                    table = list_obj.table_name
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT COUNT(*) FROM \"{table}\" WHERE data->>'{fk}' = %s AND (data->>'_is_deleted' IS NULL OR data->>'_is_deleted' = 'false')",
                            [str(value)]
                        )
                        row = cursor.fetchone()
                        if row and row[0] > 0:
                            raise serializers.ValidationError({fk: f'值 "{value}" 已存在'})
            return data

        attrs = {
            **serializer_fields,
            'Meta': Meta,
            'create': create,
            'update': update,
            'validate': validate,
        }

        return type(f'DynamicSerializer_{list_obj.key}', (serializers.Serializer,), attrs)
