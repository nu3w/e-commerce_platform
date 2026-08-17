from django.urls import path
from .views import RegisterView, LoginView, ProfileView, CustomerTestView, SupplierTestView, DeliveryPersonnelTestView, AdminTestView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("test/customer/", CustomerTestView.as_view(), name="customer-test"),
    path("test/supplier/", SupplierTestView.as_view(), name="supplier-test"),
    path("test/delivery/", DeliveryPersonnelTestView.as_view(), name="delivery-test"),
    path("test/admin/", AdminTestView.as_view(), name="admin-test"),
]
