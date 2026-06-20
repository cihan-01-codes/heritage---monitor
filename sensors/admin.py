from django.contrib import admin
from .models import SensorData

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['data_id', 'building', 'temperature', 'humidity', 'vibration', 'recorded_at']