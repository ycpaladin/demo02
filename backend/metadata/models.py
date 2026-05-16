from django.db import models
from core.models import BaseModel


class ContentType(BaseModel):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        db_table = 'content_types'
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def get_all_fields(self):
        from metadata.managers import ContentTypeManager
        return ContentTypeManager.resolve_fields(self)


class ContentTypeField(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='fields')
    field_type = models.ForeignKey('core.FieldType', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    search_type = models.CharField(max_length=20, blank=True, default='')
    order = models.IntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)
    validators = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'content_type_fields'
        ordering = ['order', 'created_at']
        unique_together = [['content_type', 'key']]

    def save(self, *args, **kwargs):
        if not self.search_type:
            from core.registry import field_type_registry
            self.search_type = field_type_registry.get_search_type(self.field_type.key) or ''
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.field_type.name})'


class List(BaseModel):
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=200)
    table_name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lists'
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def get_all_fields(self):
        from metadata.managers import ContentTypeManager
        from collections import OrderedDict
        fields = OrderedDict()

        if self.content_type:
            for f in ContentTypeManager.resolve_fields(self.content_type):
                fields[f['key']] = f

        for f in self.fields.all():
            fields[f.key] = {
                'name': f.name,
                'key': f.key,
                'field_type': f.field_type,
                'field_type__key': f.field_type.key,
                'required': f.required,
                'unique': f.unique,
                'searchable': f.searchable,
                'search_type': f.search_type,
                'order': f.order,
                'config': f.config,
                'validators': f.validators,
            }

        return list(fields.values())


class ListField(BaseModel):
    config = models.JSONField(default=dict, blank=True)
    validators = models.JSONField(default=list, blank=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='fields')
    field_type = models.ForeignKey('core.FieldType', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    search_type = models.CharField(max_length=20, blank=True, default='')
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'list_fields'
        ordering = ['order', 'created_at']
        unique_together = [['list', 'key']]

    def save(self, *args, **kwargs):
        if not self.search_type:
            from core.registry import field_type_registry
            self.search_type = field_type_registry.get_search_type(self.field_type.key) or ''
        super().save(*args, **kwargs)


class ListView(BaseModel):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='views')
    name = models.CharField(max_length=200)
    url_key = models.CharField(max_length=100, default='default')
    is_default = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'list_views'
        ordering = ['order', 'created_at']
        unique_together = [['list', 'url_key']]

    def __str__(self):
        return self.name
