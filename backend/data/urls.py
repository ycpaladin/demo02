from django.urls import path, re_path
from data.views import DynamicRecordView, DynamicRecordDetailView, DynamicRecordBatchView
from data.trash import TrashView

urlpatterns = [
    path('apps/<uuid:app_id>/lists/<uuid:list_id>/records/', DynamicRecordView.as_view()),
    path('apps/<uuid:app_id>/lists/<uuid:list_id>/records/batch/', DynamicRecordBatchView.as_view()),
    path('apps/<uuid:app_id>/lists/<uuid:list_id>/records/<uuid:record_id>/', DynamicRecordDetailView.as_view()),
    path('apps/<uuid:app_id>/trash/', TrashView.as_view()),
    path('apps/<uuid:app_id>/trash/<uuid:item_id>/', TrashView.as_view()),
]
