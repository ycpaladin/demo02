from rest_framework import serializers
from metadata.models import ContentType, ContentTypeField, List, ListField, ListView


class ContentTypeFieldSerializer(serializers.ModelSerializer):
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


class ListFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListField
        fields = '__all__'
        read_only_fields = ['id', 'list', 'created_at', 'updated_at']


class ListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListView
        fields = '__all__'
        read_only_fields = ['id', 'list', 'created_at']


class ListSerializer(serializers.ModelSerializer):
    fields = ListFieldSerializer(many=True, read_only=True)
    views = ListViewSerializer(many=True, read_only=True)
    url = serializers.CharField(required=False, allow_blank=True, max_length=200)

    class Meta:
        model = List
        fields = '__all__'
        read_only_fields = ['id', 'application', 'table_name', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
