from rest_framework import viewsets
from applications.models import Application, Navigation
from applications.serializers import ApplicationSerializer, NavigationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        qs = Application.objects.all()
        if self.action != 'list':
            return qs
        parent = self.request.query_params.get('parent', None)
        if parent is not None:
            return qs.filter(parent_id=parent)
        return qs.filter(parent__isnull=True)


class NavigationViewSet(viewsets.ModelViewSet):
    serializer_class = NavigationSerializer

    def get_queryset(self):
        return Navigation.objects.filter(application_id=self.kwargs['app_id'])

    def perform_create(self, serializer):
        serializer.save(application_id=self.kwargs['app_id'])
