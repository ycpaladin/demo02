from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metadata.views import (
    ContentTypeViewSet, ContentTypeFieldViewSet,
    ListViewSet,
)

router = DefaultRouter()
router.register(r'content-types', ContentTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('content-types/<uuid:ct_id>/fields/', ContentTypeFieldViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('content-types/<uuid:ct_id>/fields/reorder/', ContentTypeFieldViewSet.as_view({'post': 'reorder'})),
    path('content-types/<uuid:ct_id>/fields/<uuid:pk>/', ContentTypeFieldViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('apps/<uuid:app_id>/lists/', ListViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('apps/<uuid:app_id>/lists/<uuid:pk>/', ListViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('apps/<uuid:app_id>/lists/<uuid:pk>/form_schema/', ListViewSet.as_view({'get': 'form_schema'})),
    path('apps/<uuid:app_id>/lists/<uuid:pk>/schema/', ListViewSet.as_view({'get': 'schema_view', 'put': 'schema_view'})),
]
