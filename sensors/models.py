from django.db import models
from buildings.models import Building

class SensorData(models.Model):
    data_id = models.AutoField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='sensor_data')
    temperature = models.FloatField()
    humidity = models.FloatField()
    vibration = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reading {self.data_id} - {self.building.name}"

    def save_reading(self):
        self.save()
        return True

    def validate_payload(self):
        return all([
            self.temperature is not None,
            self.humidity is not None,
            self.vibration is not None,
        ])