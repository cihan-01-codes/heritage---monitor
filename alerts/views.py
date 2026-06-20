import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Alert


@login_required
def alert_list(request):
    user = request.user
    if user.role in ['Admin', 'Antiquities']:
        alerts = Alert.objects.all().order_by('-sent_at')
    else:
        alerts = Alert.objects.filter(
            building__user=user
        ).order_by('-sent_at')
    return render(request, 'alerts/alert_list.html', {'alerts': alerts})


@login_required
def export_alerts_csv(request):
    user = request.user
    if user.role in ['Admin', 'Antiquities']:
        alerts = Alert.objects.all().order_by('-sent_at')
    else:
        alerts = Alert.objects.filter(building__user=user).order_by('-sent_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alerts_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Alert ID', 'Building', 'Severity', 'Message', 'Sent At'])
    for a in alerts:
        writer.writerow([a.alert_id, a.building.name, a.severity, a.message, a.sent_at])
    return response