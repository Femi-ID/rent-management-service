from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from tickets.models import Ticket
import logging
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Ticket)
def send_ticket_email(sender, instance, created, **kwargs):
    try:
        unit = instance.unit
        landlord_email = unit.house.owner.email if unit.house.owner.email else None
        tenant_email = unit.occupant.email if unit.occupant.email else None
        
        if created and landlord_email:
            # Send email to landlord when ticket is created
           send_mail(
                subject='New Ticket Created',
                message=f'A new ticket has been created for unit {unit.unit_number}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[landlord_email],
            )

        elif instance.status == 'Resolved' and tenant_email:
            # Send email to tenant when ticket is resolved
            send_mail(
                subject='Ticket Resolved',
                message=f'Your ticket for unit {unit.unit_number} has been resolved',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[tenant_email],
            )


    except Exception as e:
        logger.error(f"Error sending email: {e}")
