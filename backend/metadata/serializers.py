from rest_framework import serializers
from metadata.models import ContentType, ContentTypeField, List


class ContentTypeFieldSerializer(serializers.ModelSerializer):
    field_type__key = serializers.CharField(source='field_type.key', read_only=True)
    field_type__name = serializers.CharField(source='field_type.name', read_only=True)

    class Meta:
        model = ContentTypeField
        fields = '__all__'
        read_only_fields = ['id', 'content_type', 'created_at', 'updated_at']


class ContentTypeSerializer(serializers.ModelSerializer):
    fields = ContentTypeFieldSerializer(many=True, read_only=True)

    class Meta:
        model = ContentType
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = '__all__'
        read_only_fields = ['id', 'application', 'table_name', 'schema', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
