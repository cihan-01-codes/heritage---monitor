from django.db import models
from accounts.models import User


class Building(models.Model):
    building_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location_gps = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buildings')

    def __str__(self):
        return self.name

    def calculate_live_vulnerability_index(self):
        from alerts.models import Alert
        recent_alerts = list(Alert.objects.filter(
            building=self
        ).order_by('-sent_at')[:10])

        if not recent_alerts:
            return 'Low'

        critical_count = sum(1 for a in recent_alerts if a.severity == 'Critical')
        warning_count = sum(1 for a in recent_alerts if a.severity == 'Warning')

        score = (critical_count * 3) + (warning_count * 1)

        if score >= 6:
            return 'High'
        elif score >= 3:
            return 'Medium'
        else:
            return 'Low'

    def fetch_associated_telemetry(self):
        return list(self.sensor_data.all())