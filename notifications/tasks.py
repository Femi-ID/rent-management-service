from datetime import timedelta, timezone
from celery import shared_task
from notifications.utils import send_notification
from core.models import LeaseAgreement, HouseUnit
from django.core.mail import send_mail
from users.models import User

@shared_task
def check_rent_due_date(self):
    today_date = timezone.now().date() # get the current date
    
    # Check for rent due in 30 days
    rent_due_soon = LeaseAgreement.objects.filter(rent_due_date = today_date + timedelta(days=30)) # get all lease agreements with rent due in 30 days

    #send email to the tenant
    for lease in rent_due_soon:
        send_notification(
        lease.user, 
        "Your rent is due soon",
        f"Dear {lease.user.full_name}, your rent for the lease {lease.id} is due on {lease.rent_due_date}. Please ensure payment is made in due time."
    )



    # check for rent due today
    rent_due = LeaseAgreement.objects.filter(rent_due_date = today_date) # get all lease agreements with rent due today

    #send email to the tenant
    for lease in rent_due:
        send_notification(
        lease.user, 
        "Your rent is due today",
        f"Dear {lease.user.full_name}, your rent for the lease {lease.id} is due today. Please ensure payment is made in due time."
    )
        

    # check for rent due in 1 day
    rent_due_tomorrow = LeaseAgreement.objects.filter(rent_due_date = today_date + timedelta(days=1))

    #send email to the tenant
    for lease in rent_due_tomorrow:
        send_notification(
        lease.user, 
        "Your rent is due tomorrow",
        f"Dear {lease.user.full_name}, your rent for the lease {lease.id} is due tomorrow. Please ensure payment is made in due time."
    )
        
    
    # check for rent overdue
    rent_overdue = LeaseAgreement.objects.filter(rent_due_date__lt = today_date)

    #send email to the tenant
    for lease in rent_overdue:
        send_notification(
        lease.user, 
        "Your rent is overdue",
        f"Dear {lease.user.full_name}, your rent for the lease {lease.id} was due on {lease.rent_due_date}. Please ensure payment is made in due time to avoid penalties."
    )



@shared_task
def send_ticket_notification_to_tenant(tenant_id, unit_id):
    print('entered send_ticket_notification_to_tenant')
    # Retrieve tenant and unit based on their IDs
    tenant = User.objects.get(id=tenant_id)
    unit = HouseUnit.objects.get(id=unit_id)
    

    # Send email to the tenant
    print('Email sent successfully 1')
    send_mail(
        f'Ticket {unit.pk} Status Updated',
        f'The status of your ticket "{unit.subject}" has been updated to "open".',
        'process.env.EMAIL_HOST_USER', #change to your email
        [tenant.email],
    )
    

@shared_task
# send mail to landlord when a tenants makes a ticket
def send_ticket_notification_to_landlord(user_id, unit_id):

    # Retrieve user and unit based on their IDs
    user = User.objects.get(id=user_id)
    house_unit = HouseUnit.objects.get(id=unit_id)
    send_mail(
        'New Ticket Notification',
        f'Your tenant: {user.email} has made a ticket for {house_unit.unit_number}.',
        'process.env.EMAIL_HOST_USER', #change to your email host user
        [house_unit.house.owner.email],   
        fail_silently=False,
    )


@shared_task
def send_email_upon_payment(user_id, house_unit_id):
    # Retrieve user and house_unit based on their IDs
    user = User.objects.get(id=user_id)
    house_unit = HouseUnit.objects.get(id=house_unit_id)

    # Send email to the landlord
    send_mail(
        'Rent Payment Notification',
        f'Your tenant: {user.email} has paid their rent for {house_unit.unit_number}.',
        'process.env.EMAIL_HOST_USER', #change to your email host user
        [house_unit.house.owner.email],   
        fail_silently=False,
    )
