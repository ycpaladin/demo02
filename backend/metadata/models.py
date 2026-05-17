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
    table_name = models.CharField(max_length=200)
    schema = models.JSONField(default=dict, blank=True)
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

        for f in self.schema.get('fields', []):
            fields[f['key']] = {
                'id': f.get('id'),
                'name': f['name'],
                'key': f['key'],
                'field_type__key': f['field_type'],
                'required': f.get('required', False),
                'unique': f.get('unique', False),
                'searchable': f.get('searchable', False),
                'search_type': f.get('search_type', ''),
                'order': f.get('order', 0),
                'config': f.get('config', {}),
                'validators': f.get('validators', []),
            }

        return list(fields.values())

    def get_extension_fields(self):
        """返回扩展字段列表（不含继承字段）"""
        return self.schema.get('fields', [])

    def set_extension_fields(self, fields):
        """整体替换扩展字段"""
        schema = self.schema or {}
        schema['fields'] = fields
        self.schema = schema

    def get_views(self):
        return self.schema.get('views', [])

    def get_view_by_key(self, url_key):
        for v in self.schema.get('views', []):
            if v.get('url_key') == url_key:
                return v
        return None
