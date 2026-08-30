from decimal import Decimal

from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, OrderItem
from .serializers import OrderSerializer

from cart.models import Cart

from notifications.email_utils import send_order_email


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    # Enable filtering for orders
    filter_backends = [DjangoFilterBackend]
    
    # Admin can filter orders by status and customer
    filterset_fields = {
        "status": ["exact"],
        "customer": ["exact"],
    }

    def get_queryset(self):

        # Customers can only see their own orders
        if self.request.user.role == "customer":
            return Order.objects.filter(
                customer=self.request.user
            ).prefetch_related("items__product")

        # Admins can see all orders
        if self.request.user.role == "admin":
            return Order.objects.all().prefetch_related(
                "items__product"
            )

        # Other roles do not get access yet
        return Order.objects.none()

    def create(self, request, *args, **kwargs):

        # Only customers can checkout
        if request.user.role != "customer":
            return Response(
                {
                    "detail": "Only customers can create orders."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the customer's cart
        try:
            cart = Cart.objects.prefetch_related(
                "items__product"
            ).get(
                customer=request.user
            )
        except Cart.DoesNotExist:
            return Response(
                {
                    "detail": "You do not have a cart."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # A checkout cannot happen with an empty cart
        cart_items = list(cart.items.all())

        if not cart_items:
            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use a database transaction so that either the entire checkout succeeds or nothing is changed.
        with transaction.atomic():

            # Create the order
            order = Order.objects.create(
                customer=request.user,
                status="pending",
                total_price=Decimal("0.00")
            )

            total_price = Decimal("0.00")

            for cart_item in cart_items:

                product = cart_item.product

                # Make sure enough stock exists
                if cart_item.quantity > product.stock:
                    return Response(
                        {
                            "detail": (
                                f"Not enough stock for "
                                f"{product.name}."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Save the current product price as the order item's price.
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.price
                )

                # Calculate order total
                total_price += (
                    product.price * cart_item.quantity
                )

                # Reduce product stock
                product.stock -= cart_item.quantity
                product.save(
                    update_fields=["stock"]
                )

            # Save final order total
            order.total_price = total_price
            order.save(
                update_fields=["total_price"]
            )

            # Empty the cart after successful checkout
            cart.items.all().delete()

        serializer = self.get_serializer(order)

        send_order_email(
            request.user,
            "Order Confirmation",
            (
                f"Thank you for you order!\n\n"
                f"Order ID: #{order.id}\n"
                f"Total: {order.total_price}\n"
                f"Status: {order.status}\n\n"
                "We will notify you when your order status changes."
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):

        # Only admins can modify orders for now
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can modify orders."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

    def partial_update(self, request, *args, **kwargs):

        # Only admins can modify orders for now
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can modify orders."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(
            request,
            *args,
            **kwargs
        )

    def destroy(self, request, *args, **kwargs):

        # Orders should not normally be deleted
        return Response(
            {
                "detail": "Orders cannot be deleted."
            },
            status=status.HTTP_403_FORBIDDEN
        )