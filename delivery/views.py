from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Delivery
from .serializers import DeliverySerializer
from notifications.models import Notification
from notifications.email_utils import send_order_email, send_delivery_assignment_email

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
        
        # Notify the delivery personnel automatically
        Notification.objects.create(
            user=delivery.delivery_person,
            title="New Delivery Assigned",
            message=f"Order #{delivery.order.id} has been assigned to you."
        )
        
        # send email to the delivery personnel
        send_delivery_assignment_email(
            delivery.delivery_person,
            delivery.order
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
                
            return self._update_delivery_status(
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
                
            return self._update_delivery_status(
                delivery,
                request
            )
            
        return Response(
            {
                "detail": "You do not have permission to modify this delivery."
            },
            status=status.HTTP_403_FORBIDDEN
        )
        
    def _update_delivery_status(self, delivery, request):
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
            
        # Don't create duplicate notifications if the same status is submitted again
        old_status = delivery.status
        
        if new_status == old_status:
            return Response(
                {
                    "detail": f"Delivery is already {new_status}."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        delivery.status = new_status
        
        if new_status == "picked":
            delivery.order.status = "confirmed"
            delivery.order.save(
                update_fields=["status"]
            )
            
            Notification.objects.create(
                user=delivery.order.customer,
                title="Order Picked Up",
                message=f"Your order #{delivery.order.id} has been picked up by the delivery personnel."
            )
            
            send_order_email(
                delivery.order.customer,
                "Your Order Has Been Picked Up",
                (
                    f"Your order #{delivery.order.id} has been picked up by the delivery personnel."
                )
            )
            
        elif new_status == "delivering":
            delivery.order.status = "shipped"
            delivery.order.save(
                update_fields=["status"]
            )
            
            Notification.objects.create(
                user=delivery.order.customer,
                title="Order Shipped",
                message=f"Your order #{delivery.order.id} is now out for delivery."
            )
            
            send_order_email(
                delivery.order.customer,
                "Your Order Is Out for Delivery",
                (
                    f"Your order #{delivery.order.id} is now out for delivery."
                )
            )
            
        elif new_status == "delivered":
            delivery.delivered_at = timezone.now()
            
            delivery.order.status = "delivered"
            
            delivery.order.save(
                update_fields=["status"]
            )
            
            Notification.objects.create(
                user=delivery.order.customer,
                title="Order Delivered",
                message=f"Your order #{delivery.order.id} has been delivered successfully."
            )
            
            send_order_email(
                delivery.order.customer,
                "Your Order Has Been Delivered",
                (
                    f"Your order #{delivery.order.id} has been delivered successfully"
                )
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