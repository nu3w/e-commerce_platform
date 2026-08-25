from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):

    # Display the product name
    product_name = serializers.CharField(source="product.name", read_only=True)

    # Calculate item subtotal
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
            "subtotal",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "price",
            "subtotal",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):

    # Display all items belonging to the order
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order

        fields = [
            "id",
            "customer",
            "status",
            "total_price",
            "items",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "total_price",
            "items",
            "created_at",
        ]