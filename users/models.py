from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("supplier", "Supplier"),
        ("customer", "Customer"),
        ("delivery", "Delivery Personnel"),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    def __str__(self):
        return self.username