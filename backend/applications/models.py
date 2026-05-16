from django.db import models
from core.models import BaseModel


class Application(BaseModel):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'applications'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name


class Navigation(BaseModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='navigations')
    name = models.CharField(max_length=200)
    link_type = models.CharField(max_length=20, choices=[('list', '列表'), ('custom_url', '自定义链接')])
    list = models.ForeignKey('metadata.List', on_delete=models.SET_NULL, null=True, blank=True)
    custom_url = models.CharField(max_length=500, blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'navigations'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name
