from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Building
from accounts.models import User


@login_required
def building_list(request):
    user = request.user
    if user.role in ['Admin', 'Antiquities']:
        buildings = Building.objects.all()
    else:
        buildings = Building.objects.filter(user=user)
    return render(request, 'buildings/building_list.html', {'buildings': buildings})


@login_required
def building_create(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    error = None
    owners = User.objects.filter(role='Owner')
    if request.method == 'POST':
        name = request.POST.get('name')
        location_gps = request.POST.get('location_gps')
        user_id = request.POST.get('user_id')
        owner = get_object_or_404(User, pk=user_id)
        Building.objects.create(name=name, location_gps=location_gps, user=owner)
        messages.success(request, f'Building {name} created successfully')
        return redirect('building_list')
    return render(request, 'buildings/building_create.html', {'owners': owners, 'error': error})


@login_required
def building_edit(request, building_id):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    building = get_object_or_404(Building, pk=building_id)
    owners = User.objects.filter(role='Owner')
    if request.method == 'POST':
        building.name = request.POST.get('name')
        building.location_gps = request.POST.get('location_gps')
        user_id = request.POST.get('user_id')
        building.user = get_object_or_404(User, pk=user_id)
        building.save()
        messages.success(request, f'Building {building.name} updated')
        return redirect('building_list')
    return render(request, 'buildings/building_edit.html', {'building': building, 'owners': owners})


@login_required
def building_delete(request, building_id):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    building = get_object_or_404(Building, pk=building_id)
    building.delete()
    messages.success(request, 'Building deleted')
    return redirect('building_list')