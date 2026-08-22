from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet

router = DefaultRouter()

router.register("carts", CartViewSet, basename="cart")
router.register("cart-items", CartItemViewSet, basename="cart-item")

urlpatterns = router.urls