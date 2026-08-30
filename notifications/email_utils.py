from django.core.mail import send_mail
from django.conf import settings

from .models import Notification

LOW_STOCK_THRESHOLD = 5

def send_order_email(customer, subject, message):
    
    # Send an email to the customer about an update to their order.
    # Make sure the customer has an email address
    if not customer.email:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer.email],
        fail_silently=False
    )
    
def send_delivery_assignment_email(delivery_person, order):
    
    # Notify delivery personnel when a new delivery is assigned
    
    if not delivery_person.email:
        return 
        
    send_mail(
        subject="New Delivery Assigned",
        message=(
            f"Order #{order.id} has been assigned to you.\n\n"
            f"Order total: {order.total_price}\n"
            "Please check your delivery dashboard for more information."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[delivery_person.email],
        fail_silently=False,
    )
    
def notify_low_stock(product):
    
    # Notify the supplier when a product has low stock.
    
    if product.stock > LOW_STOCK_THRESHOLD:
        return

    supplier = product.supplier

    # Prevent duplicate unread low-stock notifications
    existing_notification = Notification.objects.filter(
        user=supplier,
        title="Low Stock Alert",
        message__icontains=product.name,
        is_read=False
    ).exists()

    if existing_notification:
        return

    message = (
        f"Your product '{product.name}' is running low on stock.\n\n"
        f"Current stock: {product.stock}\n"
        f"Low-stock threshold: {LOW_STOCK_THRESHOLD}\n\n"
        "Please restock this product soon."
    )

    # Create in-app notification
    Notification.objects.create(
        user=supplier,
        title="Low Stock Alert",
        message=message
    )

    # Send email notification
    if supplier.email:
        send_mail(
            subject="Low Stock Alert",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[supplier.email],
            fail_silently=False,
        )