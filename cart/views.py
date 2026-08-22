from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ModelViewSet):

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        # Customers can only see their own cart
        if self.request.user.role == "customer":
            return Cart.objects.filter(
                customer=self.request.user
            )

        # Other roles cannot access customer carts
        return Cart.objects.none()

    def create(self, request, *args, **kwargs):

        # Only customers can create carts
        if request.user.role != "customer":
            return Response(
                {
                    "detail": "Only customers can create carts."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the customer already has a cart
        if Cart.objects.filter(
            customer=request.user
        ).exists():
            return Response(
                {
                    "detail": "You already have a cart."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create cart for the logged-in customer
        cart = Cart.objects.create(
            customer=request.user
        )

        serializer = self.get_serializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Cart cannot be modified directly."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def partial_update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Cart cannot be modified directly."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Cart cannot be deleted."
            },
            status=status.HTTP_403_FORBIDDEN
        )


class CartItemViewSet(viewsets.ModelViewSet):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        # Customers can only see items in their own cart
        if self.request.user.role == "customer":
            return CartItem.objects.filter(
                cart__customer=self.request.user
            )

        return CartItem.objects.none()

    def create(self, request, *args, **kwargs):

        # Only customers can add products to cart
        if request.user.role != "customer":
            return Response(
                {
                    "detail": "Only customers can add items to cart."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # If customer don't have cart, create it automatically.
        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        # Check if this product is already in the cart
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        if existing_item:

            new_quantity = (
                existing_item.quantity + quantity
            )

            if new_quantity > product.stock:
                return Response(
                    {
                        "detail": "Requested quantity exceeds available stock."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            existing_item.quantity = new_quantity
            existing_item.save()

            return Response(
                CartItemSerializer(existing_item).data,
                status=status.HTTP_200_OK
            )

        # Check stock before creating a new cart item
        if quantity > product.stock:
            return Response(
                {
                    "detail": "Requested quantity exceeds available stock."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save item into customer's cart
        cart_item = serializer.save(
            cart=cart
        )

        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):

        # Only customers can modify cart items
        if request.user.role != "customer":
            return Response(
                {
                    "detail": "Only customers can modify cart items."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        item = self.get_object()

        quantity = request.data.get(
            "quantity",
            item.quantity
        )

        if int(quantity) > item.product.stock:
            return Response(
                {
                    "detail": "Requested quantity exceeds available stock."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

    def partial_update(self, request, *args, **kwargs):

        # Only customers can modify cart items
        if request.user.role != "customer":
            return Response(
                {
                    "detail": "Only customers can modify cart items."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        item = self.get_object()

        quantity = request.data.get(
            "quantity",
            item.quantity
        )

        if int(quantity) > item.product.stock:
            return Response(
                {
                    "detail": "Requested quantity exceeds available stock."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(
            request,
            *args,
            **kwargs
        )

    def destroy(self, request, *args, **kwargs):

        # Only customers can remove cart items
        if request.user.role != "customer":
            return Response(
                {
                    "detail": "Only customers can remove cart items."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )