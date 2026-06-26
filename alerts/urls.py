from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/export/', views.export_alerts_csv, name='export_alerts_csv'),
    path('alerts/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
]