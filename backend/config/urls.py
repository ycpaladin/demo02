from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls')),
    path('api/', include('applications.urls')),
    path('api/', include('metadata.urls')),
    path('api/', include('data.urls')),
]
