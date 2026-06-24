from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sensor-data/', include('sensors.urls')),
    path('readings/', include('sensors.urls')),
    path('', include('accounts.urls')),
    path('', include('buildings.urls')),
    path('', include('alerts.urls')),
    path('', include('threshold_config.urls')),
]