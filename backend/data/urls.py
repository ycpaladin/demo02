from django.urls import path, re_path
from data.views import DynamicRecordView, DynamicRecordDetailView, DynamicRecordBatchView
from data.trash import TrashView

urlpatterns = [
    re_path(r'^apps/(?P<app_id>[0-9a-f-]+)/lists/(?P<list_url>[^/]+)/records/$', DynamicRecordView.as_view()),
    re_path(r'^apps/(?P<app_id>[0-9a-f-]+)/lists/(?P<list_url>[^/]+)/records/batch/$', DynamicRecordBatchView.as_view()),
    re_path(r'^apps/(?P<app_id>[0-9a-f-]+)/lists/(?P<list_url>[^/]+)/records/(?P<record_id>[0-9a-f-]+)/$', DynamicRecordDetailView.as_view()),
    path('apps/<uuid:app_id>/trash/', TrashView.as_view()),
    path('apps/<uuid:app_id>/trash/<uuid:item_id>/', TrashView.as_view()),
]
