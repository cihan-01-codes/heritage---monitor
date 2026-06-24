from django.db import models


class ThresholdSetting(models.Model):
    PARAMETER_CHOICES = [
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('vibration', 'Vibration'),
    ]
    parameter = models.CharField(max_length=20, choices=PARAMETER_CHOICES, unique=True)
    warning_limit = models.FloatField()
    critical_multiplier = models.FloatField(default=1.2)
    unit = models.CharField(max_length=10, default='')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parameter} — Warning: {self.warning_limit}"

    @property
    def critical_limit(self):
        return round(self.warning_limit * self.critical_multiplier, 2)