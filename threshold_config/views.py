from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ThresholdSetting


def get_or_create_defaults():
    defaults = [
        ('temperature', 40.0, 1.2, '°C'),
        ('humidity', 80.0, 1.2, '%'),
        ('vibration', 0.8, 1.2, ''),
    ]
    for param, warning, multiplier, unit in defaults:
        ThresholdSetting.objects.get_or_create(
            parameter=param,
            defaults={
                'warning_limit': warning,
                'critical_multiplier': multiplier,
                'unit': unit,
            }
        )


@login_required
def settings_view(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')

    get_or_create_defaults()
    thresholds = ThresholdSetting.objects.all().order_by('parameter')

    if request.method == 'POST':
        for threshold in thresholds:
            warning_key = f'warning_{threshold.parameter}'
            multiplier_key = f'multiplier_{threshold.parameter}'
            warning_val = request.POST.get(warning_key)
            multiplier_val = request.POST.get(multiplier_key)
            if warning_val and multiplier_val:
                threshold.warning_limit = float(warning_val)
                threshold.critical_multiplier = float(multiplier_val)
                threshold.save()
        messages.success(request, 'Threshold settings updated successfully')
        return redirect('settings')

    return render(request, 'threshold_config/settings.html', {'thresholds': thresholds})