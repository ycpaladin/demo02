from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import FieldTypeViewSet, FieldValidatorViewSet

router = DefaultRouter()
router.register(r'field-types', FieldTypeViewSet)
router.register(r'validators', FieldValidatorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
