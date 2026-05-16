from django.urls import path, include
from rest_framework.routers import DefaultRouter
from applications.views import ApplicationViewSet, NavigationViewSet

router = DefaultRouter()
router.register(r'apps', ApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),
    path('apps/<uuid:app_id>/navigations/', NavigationViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('apps/<uuid:app_id>/navigations/<uuid:pk>/', NavigationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
]
