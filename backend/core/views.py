from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from core.models import FieldType, FieldValidator
from core.serializers import FieldTypeSerializer, FieldValidatorSerializer


class FieldTypeViewSet(viewsets.ModelViewSet):
    queryset = FieldType.objects.all()
    serializer_class = FieldTypeSerializer

    def perform_destroy(self, instance):
        if instance.builtin:
            raise MethodNotAllowed('DELETE', detail='内置字段类型不可删除')
        instance.delete()


class FieldValidatorViewSet(viewsets.ModelViewSet):
    queryset = FieldValidator.objects.all()
    serializer_class = FieldValidatorSerializer

    def perform_destroy(self, instance):
        if instance.builtin:
            raise MethodNotAllowed('DELETE', detail='内置验证器不可删除')
        instance.delete()
