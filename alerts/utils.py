from .models import ThresholdLog, Alert

LIMITS = {
    'temperature': 40.0,
    'humidity': 80.0,
    'vibration': 0.8,
}

def check_thresholds(reading):
    building = reading.building
    checks = {
        'temperature': reading.temperature,
        'humidity': reading.humidity,
        'vibration': reading.vibration,
    }
    for param, value in checks.items():
        limit = LIMITS[param]
        if value >= limit:
            severity = 'Critical' if value >= limit * 1.2 else 'Warning'
            message = f"{param.capitalize()} {severity}: {value} (limit: {limit}) at {building.name}"
            threshold_log, _ = ThresholdLog.objects.get_or_create(
                building=building,
                parameter_type=param,
                defaults={'calculated_average': value, 'critical_limit': limit}
            )
            threshold_log.calculated_average = value
            threshold_log.save()
            alert = Alert.objects.create(
                building=building,
                threshold_log=threshold_log,
                severity=severity,
                message=message,
            )
            try:
                alert.dispatch_sms_via_twilio()
            except Exception:
                pass