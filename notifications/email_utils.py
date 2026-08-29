from django.core.mail import send_mail
from django.conf import settings

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