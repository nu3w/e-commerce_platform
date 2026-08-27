from rest_framework import serializers

from .models import Delivery

class DeliverySerializer(serializers.ModelSerializer):
    
    # Display customer username
    customer_name = serializers.CharField(
        source="order.customer.username",
        read_only=True
    )
    
    # Display delivery person's username
    delivery_person_name = serializers.CharField(
        source="delivery_person.username",
        read_only=True
    )
    
    # Display order total
    order_total = serializers.DecimalField(
        source="order.total_price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Delivery
        fields = [
            "id",
            "order",
            "customer_name",
            "order_total",
            "delivery_person",
            "delivery_person_name",
            "status",
            "assigned_at",
            "delivered_at",
        ]
        
        read_only_fields = [
            "id",
            "customer_name",
            "order_total",
            "delivery_person_name",
            "assigned_at",
            "delivered_at",
        ]