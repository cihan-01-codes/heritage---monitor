from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


def generate_temp_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Antiquities', 'Antiquities'),
        ('Partner', 'Partner'),
        ('Owner', 'Owner'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    must_change_password = models.BooleanField(default=True)
    temp_password = models.CharField(max_length=100, blank=True, null=True)

    def authorize_dashboard_view(self):
        return self.role

    def verify_building_access(self, building_id):
        if self.role in ['Admin', 'Antiquities']:
            return True
        return self.buildings.filter(building_id=building_id).exists()