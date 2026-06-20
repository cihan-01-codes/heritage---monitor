from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Antiquities', 'Antiquities'),
        ('Partner', 'Partner'),
        ('Owner', 'Owner'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)

    def authorize_dashboard_view(self):
        return self.role

    def verify_building_access(self, building_id):
        if self.role == 'Admin' or self.role == 'Antiquities':
            return True
        return self.buildings.filter(building_id=building_id).exists()