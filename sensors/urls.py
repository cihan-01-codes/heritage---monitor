from django.urls import path
from . import views

urlpatterns = [
    path('', views.receive_sensor_data, name='receive_sensor_data'),
    path('export/', views.export_sensor_csv, name='export_sensor_csv'),
]