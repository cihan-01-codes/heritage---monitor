from django.contrib import admin
from .models import Building

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['building_id', 'name', 'location_gps', 'user']