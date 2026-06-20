from django.contrib import admin
from .models import ThresholdLog, Alert

@admin.register(ThresholdLog)
class ThresholdLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'building', 'parameter_type', 'calculated_average', 'critical_limit', 'updated_at']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['alert_id', 'building', 'severity', 'message', 'sent_at']