from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metadata.views import (
    ContentTypeViewSet, ContentTypeFieldViewSet,
    ListViewSet, ListFieldViewSet, ListViewViewSet,
)

router = DefaultRouter()
router.register(r'content-types', ContentTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('content-types/<uuid:ct_id>/fields/', ContentTypeFieldViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('content-types/<uuid:ct_id>/fields/<uuid:pk>/', ContentTypeFieldViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('apps/<uuid:app_id>/lists/', ListViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('apps/<uuid:app_id>/lists/<uuid:pk>/', ListViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('lists/<uuid:list_id>/fields/', ListFieldViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('lists/<uuid:list_id>/fields/<uuid:pk>/', ListFieldViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('lists/<uuid:list_id>/views/', ListViewViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('lists/<uuid:list_id>/views/<uuid:pk>/', ListViewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
]
