from datetime import timedelta, timezone
from celery import shared_task
from notifications.utils import send_notification
from core.models import HouseUnit
from django.core.mail import send_mail
from payments.enums import PaymentStatus
from users.models import User
from payments.models import Subscription, Payment

@shared_task
def check_rent_due_date(self):
    today_date = timezone.now().date() # get the current date
    
    # Check for rent due in 30 days
    subscriptions = Subscription.objects.filter(next_payment_date = today_date + timedelta(days=30), status__in=[ PaymentStatus.PENDING, PaymentStatus.FAILED]) 
   
    #send email to the tenant
    for subscription in subscriptions:
        send_notification(
        "Upcoming Rent Due Reminder"
        f"Dear {subscription.customer.email},\n\nThis is a reminder that your rent for your unit is due soon on {subscription.next_payment_date}.\nPlease ensure timely payment to avoid late fees.\n\nThank you!"
    )



    # check for rent due today
    subscriptions = Subscription.objects.filter(next_payment_date = today_date, status__in=[ PaymentStatus.PENDING, PaymentStatus.FAILED])

    #send email to the tenant
    for subscription in subscriptions:
        send_notification(
        "Rent Due Reminder"
        f"Dear {subscription.customer.email},\n\nThis is a reminder that your rent for your unit is due today.\nPlease ensure timely payment to avoid late fees.\n\nThank you!"
    )

    # check for rent due in 1 day
    subscriptions = Subscription.objects.filter(next_payment_date = today_date + timedelta(days=1), status__in=[ PaymentStatus.PENDING, PaymentStatus.FAILED])

    #send email to the tenant
    for subscription in subscriptions:
        send_notification(
        "Rent Due Reminder"
        f"Dear {subscription.customer.email},\n\nThis is a reminder that your rent for your unit is due tomorrow.\nPlease ensure timely payment to avoid late fees.\n\nThank you!"
    )
        
    
    # check for rent overdue
    subscriptions = Subscription.objects.filter(next_payment_date__lt = today_date, status__in=[ PaymentStatus.PENDING, PaymentStatus.FAILED])

    #send email to the tenant
    for subscription in subscriptions:
        send_notification(
        "Rent Overdue Reminder"
        f"Dear {subscription.customer.email},\n\nThis is a reminder that your rent for your unit is overdue.\nPlease ensure timely payment to avoid late fees.\n\nThank you!"
    )



