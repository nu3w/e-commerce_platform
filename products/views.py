from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    # Enable filtering, searching and ordering
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    # Search products by name or category name
    search_fields = [
        "name",
        "category__name",
    ]

    # Filter products by category and price
    filterset_fields = {
        "category": ["exact"],
        "price": ["gte", "lte"],
    }

    # Fields users can use for ordering
    ordering_fields = [
        "name",
        "price",
        "added_at",
    ]

    # Default ordering: newest products first
    ordering = ["-added_at"]

    def create(self, request, *args, **kwargs):

        # Only suppliers and admins can create products
        if request.user.role not in ["supplier", "admin"]:
            return Response(
                {
                    "detail": "You do not have permission to create products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):

        # If a supplier creates the product,
        # automatically make that supplier the owner.
        if self.request.user.role == "supplier":
            serializer.save(supplier=self.request.user)

        # Admin can choose the supplier.
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):

        product = self.get_object()

        # Customers and delivery personnel cannot modify products
        if request.user.role not in ["admin", "supplier"]:
            return Response(
                {
                    "detail": "You do not have permission to modify products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Supplier can only modify their own products
        if (
            request.user.role == "supplier"
            and product.supplier != request.user
        ):
            return Response(
                {
                    "detail": "You can only modify your own products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        product = self.get_object()

        # Customers and delivery personnel cannot modify products
        if request.user.role not in ["admin", "supplier"]:
            return Response(
                {
                    "detail": "You do not have permission to modify products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Supplier can only modify their own products
        if (
            request.user.role == "supplier"
            and product.supplier != request.user
        ):
            return Response(
                {
                    "detail": "You can only modify your own products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):

        # Suppliers cannot change the owner of their products.
        # Even if they send another supplier ID,
        # the product remains assigned to themselves.
        if self.request.user.role == "supplier":
            serializer.save(supplier=self.request.user)

        # Admin is allowed to change the supplier.
        else:
            serializer.save()

    def destroy(self, request, *args, **kwargs):

        product = self.get_object()

        # Customers and delivery personnel cannot delete products
        if request.user.role not in ["admin", "supplier"]:
            return Response(
                {
                    "detail": "You do not have permission to delete products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Supplier can only delete their own products
        if (
            request.user.role == "supplier"
            and product.supplier != request.user
        ):
            return Response(
                {
                    "detail": "You can only delete your own products."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)
    

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        # Only admins can create categories
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can create categories."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        # Only admins can modify categories
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can modify categories."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        # Only admins can modify categories
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can modify categories."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):

        # Only admins can delete categories
        if request.user.role != "admin":
            return Response(
                {
                    "detail": "Only admins can delete categories."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)