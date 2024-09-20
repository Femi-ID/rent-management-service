from django.core.mail import send_mail
from users.models import User
from core.models import HouseUnit
from payments.models import Payment, Subscription, PaymentPlan
import os

def send_notification_for_rent_due(user, subject, message):
    send_mail(
        subject,
        message,
        os.getenv('EMAIL_HOST_USER'), #change to your email host user
        [user.email],   
        fail_silently=False,
    )


def send_ticket_notification_to_tenant(unit_id, landlord_id):
    try:
        unit = HouseUnit.objects.get(id=unit_id, house__owner_id=landlord_id)
    except HouseUnit.DoesNotExist:
        print('This unit does not belong to this landlord')
        return
    
    # Retrieve tenant information from payment
    latest_payment_for_unit = Payment.objects.filter(house_unit_id=unit_id).order_by('-created_at').first()

    if latest_payment_for_unit is None:
        print('No payment found for this unit') 
        return
    else:
        # Send email to the tenant
        send_mail(
            f'Ticket {unit.pk} Status Updated',
            f'The status of your ticket for {unit.unit_number} has been updated. Please login to your account to view the changes.',
            os.getenv('EMAIL_HOST_USER'), # This is the sender email
            [latest_payment_for_unit.email], # This is the receiver email
            fail_silently=False,
        )
    

# send mail to landlord when a tenants makes a ticket
def send_ticket_notification_to_landlord(tenant_id, unit_id):

    # Retrieve user and unit based on their IDs
    user = User.objects.get(id=tenant_id)
    house_unit = HouseUnit.objects.get(id=unit_id)
    send_mail(
        'New Ticket Notification',
        f'Your tenant: {user.email} has made a ticket for {house_unit.unit_number}.',
        os.getenv('EMAIL_HOST_USER') , # This is the sender email
        [house_unit.house.owner.email],   # This is the receiver email
        fail_silently=False,
    )


def send_email_upon_payment(user_id, house_unit_id):
    # Retrieve user and house_unit based on their IDs
    user = User.objects.get(id=user_id)
    house_unit = HouseUnit.objects.get(id=house_unit_id)

    # Send email to the landlord
    send_mail(
        'Rent Payment Notification',
        f'Your tenant: {user.email} has paid their rent for {house_unit.unit_number}.',
        os.getenv('EMAIL_HOST_USER'), # This is the sender email
        [house_unit.house.owner.email], # This is the receiver email
        fail_silently=False,
    )
