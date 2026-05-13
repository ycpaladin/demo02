from rest_framework import viewsets
from applications.models import Application, Navigation
from applications.serializers import ApplicationSerializer, NavigationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.filter(parent__isnull=True)
    serializer_class = ApplicationSerializer


class NavigationViewSet(viewsets.ModelViewSet):
    serializer_class = NavigationSerializer

    def get_queryset(self):
        return Navigation.objects.filter(application_id=self.kwargs['app_id'])

    def perform_create(self, serializer):
        serializer.save(application_id=self.kwargs['app_id'])
