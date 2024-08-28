from datetime import timedelta, timezone
from celery import shared_task
from notifications.utils import send_notification
from core.models import LeaseAgreement

@shared_task
def check_rent_due_date(self):
    today_date = timezone.now().date() # get the current date
    
    # Check for rent due in 30 days
    # assuming the lease agreement model has a field called due_date
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



