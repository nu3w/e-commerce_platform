from rest_framework import serializers
from .models import Category, Product
from users.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
        ]

class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.username",
        read_only=True
    )

    # Admin can provide a supplier ID when creating a product
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="supplier"), 
        required = False
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "category",
            "supplier",
            "supplier_name",
            "added_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "supplier_name",
            "added_at",
            "updated_at",
        ]