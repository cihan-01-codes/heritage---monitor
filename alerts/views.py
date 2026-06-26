import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from .models import Alert


@login_required
def alert_list(request):
    from django.core.paginator import Paginator
    from django.utils.dateparse import parse_date

    user = request.user
    if user.role in ['Admin', 'Antiquities']:
        alerts = Alert.objects.all().order_by('-sent_at')
    else:
        alerts = Alert.objects.filter(
            building__user=user
        ).order_by('-sent_at')

    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    severity = request.GET.get('severity', '')
    acknowledged = request.GET.get('acknowledged', '')

    if date_from:
        alerts = alerts.filter(sent_at__date__gte=parse_date(date_from))
    if date_to:
        alerts = alerts.filter(sent_at__date__lte=parse_date(date_to))
    if severity:
        alerts = alerts.filter(severity=severity)
    if acknowledged == 'yes':
        alerts = alerts.filter(acknowledged=True)
    elif acknowledged == 'no':
        alerts = alerts.filter(acknowledged=False)

    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'alerts/alert_list.html', {
        'alerts': page_obj,
        'page_obj': page_obj,
        'date_from': date_from,
        'date_to': date_to,
        'severity': severity,
        'acknowledged': acknowledged,
    })


@login_required
def acknowledge_alert(request, alert_id):
    if request.user.role not in ['Admin', 'Antiquities']:
        return redirect('alert_list')
    alert = get_object_or_404(Alert, pk=alert_id)
    alert.acknowledged = True
    alert.acknowledged_by = request.user
    alert.acknowledged_at = timezone.now()
    alert.save()
    return redirect('alert_list')


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
    writer.writerow(['Alert ID', 'Building', 'Severity', 'Message', 'Sent At', 'Acknowledged', 'Acknowledged By'])
    for a in alerts:
        writer.writerow([
            a.alert_id, a.building.name, a.severity, a.message, a.sent_at,
            'Yes' if a.acknowledged else 'No',
            a.acknowledged_by.username if a.acknowledged_by else '—'
        ])
    return response