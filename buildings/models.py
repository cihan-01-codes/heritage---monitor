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
        return "Calculated"

    def fetch_associated_telemetry(self):
        return list(self.sensor_data.all())