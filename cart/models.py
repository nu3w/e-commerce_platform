from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role":"customer"}, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())
    
    def __str__(self):
        return f"{self.customer.username}'s Cart"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["cart","product"],
            name="unique_product_per_cart"
        )]
        
    @property
    def subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} * {self.product.name}"