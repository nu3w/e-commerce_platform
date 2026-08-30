from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order, OrderItem
from products.models import Product
from delivery.models import Delivery

from drf_spectacular.utils import extend_schema

class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        
        # Only admin can access admin analytics
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can access this dashboard."
                },
                status=403
            )
            
            
        # Order Statistics
        
        total_orders = Order.objects.count()
        
        pending_orders = Order.objects.filter(
            status="pending"
        ).count()
        
        confirmed_orders = Order.objects.filter(
            status="confirmed"
        ).count()
        
        shipped_orders = Order.objects.filter(
           status="shipped" 
        ).count()
        
        delivered_orders = Order.objects.filter(
            status="delivered"
        ).count()
        
        cancelled_orders = Order.objects.filter(
            status="cancelled"
        ).count()
        
        # Total Revenue
        
        # Only completed orders count as revenue
        revenue = Order.objects.filter(
            status="delivered"
        ).aggregate(
            total=Sum("total_price")
        )["total"] or 0
        
        # Top Suppliers
        
        # Calculate how much each supplier has earned from deliveres orders.
        top_supplier_data = (
            OrderItem.objects.filter(
                order__status="delivered"
            ).values(
                "product__supplier__username"
            ).annotate(
                revenue=Sum(
                    ExpressionWrapper(
                        F("price") * F("quantity"),
                        output_field=DecimalField(
                            max_digits=12,
                            decimal_places=2
                        )
                    )
                )
            ).order_by("-revenue")
        )
        
        top_suppliers = []
        
        for supplier in top_supplier_data:
            top_suppliers.append(
                {
                    "supplier": supplier[
                        "product__supplier__username"
                    ],
                    "revenue": supplier["revenue"],
                }
            )
            
        return Response(
            {
                "total_revenue": revenue,
                "total_orders": total_orders,
                
                "order_statistics": {
                    "pending": pending_orders,
                    "confirmed": confirmed_orders,
                    "shipped": shipped_orders,
                    "delivered": delivered_orders,
                    "cancelled": cancelled_orders,
                },
                "top_suppliers": top_suppliers
            }
        )
        
class SupplierAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=dict)
    
    def get(self, request):
        
        # Only suppliers can access this dashboard
        if request.user.role != "supplier":
            return Response(
                {
                    "detail": "Only suppliers can access this dashboard."
                },
                status=403
            )
            
        # Supplier Products
        
        products = Product.objects.filter(
            supplier=request.user
        )
        
        total_products = products.count()
        
        total_stock = products.aggregate(
            total=Sum("stock")
        )["total"] or 0
        
        # Products with 5 or fewer items are considered low stock
        low_stock_products = products.filter(
            stock__lte=5
        ).count()
        
        # Delivery Statistics
        
        supplier_deliveries = Delivery.objects.filter(
            order__items__product__supplier = request.user
        ).distinct()
        
        assigned_deliveries = supplier_deliveries.filter(
            status="assigned"
        ).count()
        
        picked_deliveries = supplier_deliveries.filter(
            status="picked"
        ).count()
        
        delivering_deliveries = supplier_deliveries.filter(
            status="delivering"
        ).count()
        
        delivered_deliveries = supplier_deliveries.filter(
            status="delivered"
        ).count()
        
        return Response(
            {
                "supplier": request.user.username,
                
                "inventory": {
                    "total_products": total_products,
                    "total_stock": total_stock,
                    "low_stock_products": low_stock_products,
                },
            
                "delivery_statistics": {
                    "assigned": assigned_deliveries,
                    "picked": picked_deliveries,
                    "delivering": delivering_deliveries,
                    "delivered": delivered_deliveries,
                },
            }
        )