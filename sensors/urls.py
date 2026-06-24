from django.urls import path
from . import views

urlpatterns = [
    path('', views.receive_sensor_data, name='receive_sensor_data'),
    path('export/', views.export_sensor_csv, name='export_sensor_csv'),
    path('readings/', views.sensor_readings_list, name='sensor_readings_list'),
    path('readings/<int:building_id>/', views.sensor_readings_by_building, name='sensor_readings_by_building'),
]