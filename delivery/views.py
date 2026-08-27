from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Delivery
from .serializers import DeliverySerializer

class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        
        # Admin can see all deliveries
        if self.request.user.role == "admin":
            return Delivery.objects.all().select_related(
                "order",
                "order__customer",
                "delivery_person"
            )
            
        # Delivery personnel can only see deliveries assigned to themselves
        if self.request.user.role == "delivery":
            return Delivery.objects.filter(
                delivery_person=self.request.user
            ).select_related(
                "order",
                "order__customer",
                "delivery_person"
            )
            
        # Customers can see deliveries for their own orders
        if self.request.user.role == "customer":
            return Delivery.objects.filter(
                order__customer=self.request.user
            ).select_related(
                "order",
                "order__customer",
                "delivery_person"
            )
            
        return Delivery.objects.none()
    
    def create(self, request, *args, **kwargs):
        
        # Only admins can assign deliveries
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can assign deliveries."
                },
                status=status.HTTP_403_FORBIDDEN
            )
            
        order_id = request.data.get("order")
        delivery_person_id = request.data.get(
            "delivery_person"
        )
        
        # Make sure both values are provided
        if not order_id or not delivery_person_id:
            return Response(
                {
                    "detail": "Both order and delivery person are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate the serializer
        serializer = self.get_serializer(
            data=request.data
        )
        
        serializer.is_valid(
            raise_exception=True
        )
        
        # Save the delivery
        delivery = serializer.save(
            status="assigned"
        )
        
        return Response(
            self.get_serializer(delivery).data,
            status=status.HTTP_201_CREATED
        )
        
    def update(self, request, *args, **kwargs):
        delivery = self.get_object()
        
        # Admin can modify delivery assignments
        if request.user.role == "admin":
            return super().update(
                request,
                *args,
                **kwargs
            )
            
        # Delivery personnel can update the status of their own delivery
        if request.user.role == "delivery":
            if delivery.delivery_person != request.user:
                return Response(
                    {
                        "detail": "You can only update your own deliveries."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
                
            return self.update_delivery_status(
                delivery,
                request
            )
        
        return Response(
            {
                "detail": "You do not have permission to modify this delivery."
            },
            status=status.HTTP_403_FORBIDDEN
        )
        
    def partial_update(self, request, *args, **kwargs):
        delivery = self.get_object()
        
        # Admin can modify anything
        if request.user.role == "admin":
            return super().partial_update(
                request,
                *args,
                **kwargs
            )
            
        # Delivery personnel can update their own delivery status
        if request.user.role == "delivery":
            if delivery.delivery_person != request.user:
                return Response(
                    {
                        "detail": "You can only update your own deliveries."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
                
            return self.update_delivery_status(
                delivery,
                request
            )
            
        return Response(
            {
                "detail": "You do not have permission to modify this delivery."
            },
            status=status.HTTP_403_FORBIDDEN
        )
        
    def update_delivery_status(self, delivery, request):
        new_status = request.data.get("status")
        valid_statuses = [
            "assigned",
            "picked",
            "delivering",
            "delivered",
        ]
        
        if new_status not in valid_statuses:
            return Response(
                {
                    "detail": (
                        "Invalid delivery status. "
                        "Use assigned, picked, delivering, or delivered."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        delivery.status = new_status
        
        # When delivery is completed, save the delivery timestamp
        if new_status == "delivered":
            delivery.delivered_at = timezone.now()
            
            # Also mark the related order as delivered
            delivery.order.status = "delivered"
            
            delivery.order.save(
                update_fields=["status"]
            )
            
        elif new_status == "picked":
            
            # Order will be confirmed once delivery personnel picks it up
            delivery.order.status = "confirmed"
            
            delivery.order.save(
                update_fields=["status"]
            )
            
        elif new_status == "delivering":
            
            # Order is now on its way
            delivery.order.status = "shipped"
            
            delivery.order.save(
                update_fields=["status"]
            )
            
        delivery.save()
        
        return Response(
            self.get_serializer(delivery).data
        )
        
    def destroy(self, request, *args, **kwargs):
        
        # Deliveries should not normally be deleted
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can delete deliveries."
                },
                status=status.HTTP_403_FORBIDDEN
            )
            
        return super().destroy(
            request,
            *args,
            **kwargs
        )