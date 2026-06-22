from django.urls import path
from . import views

urlpatterns = [
    path('buildings/', views.building_list, name='building_list'),
    path('buildings/create/', views.building_create, name='building_create'),
    path('buildings/<int:building_id>/edit/', views.building_edit, name='building_edit'),
    path('buildings/<int:building_id>/delete/', views.building_delete, name='building_delete'),
    path('buildings/<int:building_id>/trends/', views.building_trends, name='building_trends'),
    path('api/buildings/<int:building_id>/stats/', views.building_stats_api, name='building_stats_api'),
]