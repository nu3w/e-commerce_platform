from django.db import models
from orders.models import Order
from django.conf import settings

class Delivery(models.Model):
    STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("picked", "Picked Up"),
        ("delivering", "Out for Delivery"),
        ("delivered", "Delivered"),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "delivery"}, related_name="deliveries")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="assigned")
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Delivery {self.order.id}"
    
