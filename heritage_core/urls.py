from django.contrib import admin
from django.urls import path, include
from sensors import views as sensor_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sensor-data/', include('sensors.urls')),
    path('api/sensor-data/simulate/', sensor_views.simulate_sensor_data, name='simulate_sensor_data'),
    path('readings/', sensor_views.sensor_readings_list, name='sensor_readings_list'),
    path('readings/<int:building_id>/', sensor_views.sensor_readings_by_building, name='sensor_readings_by_building'),
    path('simulator/', sensor_views.simulator_page, name='simulator_page'),
    path('', include('accounts.urls')),
    path('', include('buildings.urls')),
    path('', include('alerts.urls')),
    path('', include('threshold_config.urls')),
]