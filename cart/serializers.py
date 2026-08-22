from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            "id", 
            "product",
            "product_name",
            "product_price",
            "quantity",
            "subtotal",
            "added_at",
        ]
        
        read_only_fields = [
            "id",
            "product_name",
            "product_price",
            "subtotal",
            "added_at",
        ]
        
    def validate_quantity(self, value):
        
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )
            
        return value
    
    def validate_product(self, product):
        
        if product.stock <= 0:
            raise serializers.ValidationError(
                "This product is currently out of stock."
            )
            
        return product
    

class CartSerializer(serializers.ModelSerializer):
    
    items = CartItemSerializer(many=True, read_only=True)
    
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            "id",
            "customer",
            "items",
            "total_price",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields = [
            "id",
            "customer",
            "items",
            "total_price",
            "created_at",
            "updated_at",
        ]