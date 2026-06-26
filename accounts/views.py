from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from sensors.models import SensorData
from alerts.models import Alert
from buildings.models import Building
from .models import User, generate_temp_password


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.must_change_password:
                return redirect('change_password')
            return redirect('dashboard')
        else:
            error = 'Invalid credentials'
    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password_view(request):
    message = None
    error = None
    temp_pwd = None
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            temp_pwd = generate_temp_password()
            user.set_password(temp_pwd)
            user.must_change_password = True
            user.temp_password = temp_pwd
            user.save()
            message = f'Temporary password generated for {username}'
        except User.DoesNotExist:
            error = 'Username not found'
    return render(request, 'accounts/forgot_password.html', {
        'message': message,
        'error': error,
        'temp_pwd': temp_pwd,
    })


@login_required
def change_password_view(request):
    error = None
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            error = 'Passwords do not match'
        elif len(new_password) < 6:
            error = 'Password must be at least 6 characters'
        else:
            request.user.set_password(new_password)
            request.user.must_change_password = False
            request.user.temp_password = None
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully')
            return redirect('dashboard')
    return render(request, 'accounts/change_password.html', {'error': error})


@login_required
def dashboard_view(request):
    role = request.user.role if request.user.role else 'Admin'
    template_map = {
        'Admin': 'dashboard/admin_dashboard.html',
        'Antiquities': 'dashboard/antiquities_dashboard.html',
        'Partner': 'dashboard/partner_dashboard.html',
        'Owner': 'dashboard/owner_dashboard.html',
    }
    template = template_map.get(role, 'dashboard/admin_dashboard.html')
    return render(request, template, {'user': request.user})


@login_required
def dashboard_stats(request):
    user = request.user
    if user.role in ['Admin', 'Antiquities', 'Partner']:
        readings = SensorData.objects.order_by('-recorded_at')[:20]
        buildings = Building.objects.all()
    else:
        buildings = Building.objects.filter(user=user)
        readings = SensorData.objects.filter(
            building__in=buildings
        ).order_by('-recorded_at')[:20]

    readings = list(reversed(list(readings)))
    alerts = Alert.objects.order_by('-sent_at')[:5]

    return JsonResponse({
        'total_buildings': Building.objects.count(),
        'total_users': User.objects.count(),
        'total_alerts': Alert.objects.count(),
        'total_readings': SensorData.objects.count(),
        'labels': [r.recorded_at.strftime('%H:%M') for r in readings],
        'temperatures': [r.temperature for r in readings],
        'humidities': [r.humidity for r in readings],
        'vibrations': [r.vibration for r in readings],
        'recent_alerts': [{'severity': a.severity, 'message': a.message} for a in alerts],
        'my_buildings': [{'name': b.name, 'location_gps': b.location_gps} for b in buildings],
    })


@login_required
def user_list(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_create(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if User.objects.filter(username=username).exists():
            error = 'Username already exists'
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                must_change_password=True,
            )
            messages.success(request, f'User {username} created. They must change password on first login.')
            return redirect('user_list')
    return render(request, 'accounts/user_create.html', {'error': error})

@login_required
def user_edit(request, user_id):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=user_id)
    error = None
    if request.method == 'POST':
        target_user.email = request.POST.get('email')
        target_user.role = request.POST.get('role')
        target_user.phone_number = request.POST.get('phone_number')
        target_user.first_name = request.POST.get('first_name')
        target_user.last_name = request.POST.get('last_name')
        new_password = request.POST.get('password')
        if new_password:
            target_user.set_password(new_password)
            target_user.must_change_password = True
        target_user.save()
        messages.success(request, f'User {target_user.username} updated')
        return redirect('user_list')
    return render(request, 'accounts/user_edit.html', {'target_user': target_user, 'error': error})

@login_required
def user_delete(request, user_id):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=user_id)
    if target_user != request.user:
        target_user.delete()
        messages.success(request, 'User deleted')
    return redirect('user_list')


@login_required
def user_reset_password(request, user_id):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=user_id)
    temp_pwd = generate_temp_password()
    target_user.set_password(temp_pwd)
    target_user.must_change_password = True
    target_user.temp_password = temp_pwd
    target_user.save()
    messages.success(request, f'Temporary password for {target_user.username}: {temp_pwd}')
    return redirect('user_list')

@login_required
def profile_view(request):
    error = None
    success = None
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.phone_number = request.POST.get('phone_number')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password:
            if new_password != confirm_password:
                error = 'Passwords do not match'
            elif len(new_password) < 6:
                error = 'Password must be at least 6 characters'
            else:
                request.user.set_password(new_password)
                update_session_auth_hash(request, request.user)
                success = 'Profile and password updated successfully'
        if not error:
            request.user.save()
            if not success:
                success = 'Profile updated successfully'
    return render(request, 'accounts/profile.html', {
        'error': error,
        'success': success,
    })