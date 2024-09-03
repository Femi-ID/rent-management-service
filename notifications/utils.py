from django.core.mail import send_mail
from users.models import User
from core.models import HouseUnit
from payments.models import Payment

def send_notification(user, subject, message):
    send_mail(
        subject,
        message,
        'process.env.EMAIL_HOST_USER', #change to your email host user
        [user.email],   
        fail_silently=False,
    )
    print('Email sent successfully')


def send_ticket_notification_to_tenant(unit_id):
    unit = HouseUnit.objects.get(id=unit_id)
    # get user details for unit from payment
    tenant = Payment.objects.get(house_unit=unit_id).user

    # Send email to the tenant
    send_mail(
        f'Ticket {unit.pk} Status Updated',
        f'The status of your ticket "{unit.subject}" has been updated to "open".',
        'process.env.EMAIL_HOST_USER', # This is the sender email
        [tenant.email],
        #TODO: Add the tenant field to the HouseUnit model
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
        'process.env.EMAIL_HOST_USER', # This is the sender email
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
        'process.env.EMAIL_HOST_USER', # This is the sender email
        [house_unit.house.owner.email], # This is the receiver email
        fail_silently=False,
    )
