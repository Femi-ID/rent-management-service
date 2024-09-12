from datetime import timedelta, timezone
from celery import shared_task
from notifications.utils import send_notification_for_rent_due
from payments.enums import PaymentStatus
from payments.models import Subscription


@shared_task
def check_rent_due_dates():

    def send_reminders(subscription, date_before_due, reminder_class):
        subject = f"{reminder_class} Rent Due Reminder"
        message = (f"Dear {subscription.customer.email},\n\n"
        f"This is a reminder that your rent for your unit is due {reminder_class} on {subscription.next_payment_date}.\n"
        f"Please ensure timely payment to avoid late fees.\n\nThank you!")
        
        send_notification_for_rent_due(subscription.customer, subject, message)
        

    # This is a dictionary that contains the days before the next payment date that we want to send reminders
    interval = {
        'monthly': [7, 0],
        'quarterly': [30, 7, 0],
        'biannually': [30, 7, 0],
        'annually': [100, 30, 7,  0]
    }

    today_date = timezone.now().date() # get the current date


    subscriptions = Subscription.objects.filter(status__in=[ PaymentStatus.PENDING, PaymentStatus.FAILED])
    for subscription in subscriptions:
        payment_intervals = subscription.plan.interval
        if payment_intervals in interval:
            for i in interval[payment_intervals]:
                if subscription.next_payment_date == today_date + timedelta(days=i):
                    if i > 0:
                        send_reminders(subscription, i, 'Upcoming')
                    else:
                        send_reminders(subscription, i, 'Today')

  



# check the plan the tenants are subscribed to 
# check the next payment date 
# check the last payment date made by the tenant 


