from .models import ThresholdLog, Alert


def get_limits():
    try:
        from threshold_config.models import ThresholdSetting
        limits = {}
        for t in ThresholdSetting.objects.all():
            limits[t.parameter] = {
                'warning': t.warning_limit,
                'critical': t.critical_limit,
            }
        if limits:
            return limits
    except Exception:
        pass
    return {
        'temperature': {'warning': 40.0, 'critical': 48.0},
        'humidity': {'warning': 80.0, 'critical': 96.0},
        'vibration': {'warning': 0.8, 'critical': 0.96},
    }


def check_thresholds(reading):
    building = reading.building
    limits = get_limits()
    checks = {
        'temperature': reading.temperature,
        'humidity': reading.humidity,
        'vibration': reading.vibration,
    }
    for param, value in checks.items():
        warning_limit = limits[param]['warning']
        critical_limit = limits[param]['critical']
        if value >= warning_limit:
            severity = 'Critical' if value >= critical_limit else 'Warning'
            message = (
                f"{param.capitalize()} {severity}: {value} "
                f"(warning: {warning_limit}, critical: {critical_limit}) "
                f"at {building.name}"
            )
            threshold_log, _ = ThresholdLog.objects.get_or_create(
                building=building,
                parameter_type=param,
                defaults={
                    'calculated_average': value,
                    'critical_limit': critical_limit
                }
            )
            threshold_log.calculated_average = value
            threshold_log.critical_limit = critical_limit
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