from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from tickets.models import Ticket
from core.models import HouseUnit
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Ticket)
def send_ticket_email(sender, instance, created, **kwargs):
    try:
        unit = instance.unit
        landlord_email = unit.house.owner.email if unit.house.owner.email else None
        tenant_email = unit.occupant.email if unit.occupant.email else None
        
        if created and landlord_email:
            # Send email to landlord when ticket is created
            subject = 'New Ticket Created'
            context = {'unit': unit, 'ticket': instance}
            html_content = render_to_string('email/ticket_created.html', context)
            text_content = f"New ticket created for {unit.unit_number}"
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [landlord_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            logger.info(f"New ticket creation email sent to landlord at {landlord_email}")

        elif instance.status == 'Resolved' and tenant_email:
            # Send email to tenant when ticket is resolved
            subject = 'Ticket Resolved'
            context = {'unit': unit, 'ticket': instance}
            html_content = render_to_string('email/ticket_resolved.html', context)
            text_content = f"Ticket resolved for {unit.unit_number}"
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [tenant_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            logger.info(f"Ticket resolution email sent to tenant at {tenant_email}")

    except Exception as e:
        logger.error(f"Error sending email: {e}")
