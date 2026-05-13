import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FieldType(BaseModel):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    builtin = models.BooleanField(default=False)
    config_schema = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'field_types'
        ordering = ['builtin', 'created_at']

    def __str__(self):
        return self.name


class FieldValidator(BaseModel):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    builtin = models.BooleanField(default=False)
    rule_type = models.CharField(max_length=50)
    rule_config = models.JSONField(default=dict)
    error_message = models.CharField(max_length=200, default='验证失败')

    class Meta:
        db_table = 'field_validators'
        ordering = ['builtin', 'created_at']

    def __str__(self):
        return self.name
