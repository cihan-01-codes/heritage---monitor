import json
import csv
import os
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import SensorData
from buildings.models import Building
from alerts.utils import check_thresholds


@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('SENSOR_API_KEY'):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        try:
            payload = json.loads(request.body)
            building = Building.objects.get(building_id=payload['building_id'])
            reading = SensorData.objects.create(
                building=building,
                temperature=payload['temperature'],
                humidity=payload['humidity'],
                vibration=payload['vibration'],
            )
            check_thresholds(reading)
            return JsonResponse({'status': 'ok', 'data_id': reading.data_id})
        except Building.DoesNotExist:
            return JsonResponse({'error': 'Building not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def export_sensor_csv(request):
    user = request.user
    if user.role in ['Admin', 'Antiquities']:
        readings = SensorData.objects.all().order_by('-recorded_at')
    else:
        readings = SensorData.objects.filter(
            building__user=user
        ).order_by('-recorded_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sensor_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Building', 'Temperature', 'Humidity', 'Vibration', 'Recorded At'])
    for r in readings:
        writer.writerow([r.data_id, r.building.name, r.temperature, r.humidity, r.vibration, r.recorded_at])
    return response


@login_required
def sensor_readings_by_building(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    readings = SensorData.objects.filter(
        building=building
    ).order_by('-recorded_at')[:100]
    return render(request, 'sensors/readings_list.html', {
        'readings': readings,
        'buildings': Building.objects.all(),
        'selected_building': str(building_id),
        'building': building,
    })

@login_required
def sensor_readings_list(request):
    from django.core.paginator import Paginator
    from django.utils.dateparse import parse_date

    user = request.user
    if user.role in ['Admin', 'Antiquities', 'Partner']:
        buildings = Building.objects.all()
        readings = SensorData.objects.all().order_by('-recorded_at')
    else:
        buildings = Building.objects.filter(user=user)
        readings = SensorData.objects.filter(
            building__in=buildings
        ).order_by('-recorded_at')

    selected_building = request.GET.get('building', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if selected_building:
        readings = readings.filter(building__building_id=selected_building)
    if date_from:
        readings = readings.filter(recorded_at__date__gte=parse_date(date_from))
    if date_to:
        readings = readings.filter(recorded_at__date__lte=parse_date(date_to))

    paginator = Paginator(readings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sensors/readings_list.html', {
        'readings': page_obj,
        'buildings': buildings,
        'selected_building': selected_building,
        'date_from': date_from,
        'date_to': date_to,
        'page_obj': page_obj,
    })

@login_required
def simulate_sensor_data(request):
    if request.user.role != 'Admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        import json
        import random
        try:
            payload = json.loads(request.body)
            building_id = payload.get('building_id')
            mode = payload.get('mode', 'normal')

            building = Building.objects.get(building_id=building_id)

            if mode == 'normal':
                temperature = round(random.uniform(18, 35), 1)
                humidity = round(random.uniform(30, 70), 1)
                vibration = round(random.uniform(0.0, 0.5), 2)
            elif mode == 'warning':
                temperature = round(random.uniform(40, 47), 1)
                humidity = round(random.uniform(80, 95), 1)
                vibration = round(random.uniform(0.8, 0.95), 2)
            elif mode == 'critical':
                temperature = round(random.uniform(48, 65), 1)
                humidity = round(random.uniform(96, 100), 1)
                vibration = round(random.uniform(0.96, 1.5), 2)

            reading = SensorData.objects.create(
                building=building,
                temperature=temperature,
                humidity=humidity,
                vibration=vibration,
            )
            check_thresholds(reading)
            return JsonResponse({
                'status': 'ok',
                'data_id': reading.data_id,
                'temperature': temperature,
                'humidity': humidity,
                'vibration': vibration,
                'mode': mode,
            })
        except Building.DoesNotExist:
            return JsonResponse({'error': 'Building not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)

@login_required
def simulator_page(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    buildings = Building.objects.all()
    return render(request, 'sensors/simulator.html', {'buildings': buildings})