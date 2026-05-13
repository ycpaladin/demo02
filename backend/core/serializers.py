from rest_framework import serializers
from core.models import FieldType, FieldValidator


class FieldTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldType
        fields = '__all__'
        read_only_fields = ['id', 'builtin', 'created_at', 'updated_at']


class FieldValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldValidator
        fields = '__all__'
        read_only_fields = ['id', 'builtin', 'created_at', 'updated_at']
