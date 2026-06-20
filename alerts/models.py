from django.db import models
from buildings.models import Building

class ThresholdLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='threshold_logs')
    parameter_type = models.CharField(max_length=50)
    calculated_average = models.FloatField()
    critical_limit = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parameter_type} - {self.building.name}"

    def recalculate_moving_metrics(self):
        return True

    def fetch_current_limits(self):
        return self


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('Warning', 'Warning'),
        ('Critical', 'Critical'),
    ]
    alert_id = models.AutoField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='alerts')
    threshold_log = models.ForeignKey(ThresholdLog, on_delete=models.SET_NULL, null=True, related_name='alerts')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.severity} - {self.building.name}"

    def log_alert_db(self):
        self.save()
        return True

    def dispatch_sms_via_twilio(self):
        from twilio.rest import Client
        import os
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        client.messages.create(
            body=self.message,
            from_=os.getenv('TWILIO_WHATSAPP_NUMBER'),
            to='whatsapp:' + self.building.user.phone_number
        )