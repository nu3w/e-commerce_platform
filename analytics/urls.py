from django.urls import path

from .views import AdminAnalyticsView, SupplierAnalyticsView

urlpatterns = [
    path("admin/", AdminAnalyticsView.as_view(), name="admin-analytics"),
    path("supplier/", SupplierAnalyticsView.as_view(), name="supplier-analytics"),
]
