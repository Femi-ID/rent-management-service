# # use signals to send email to landlord when a new ticket is created
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from tickets.models import Ticket
# from django.core.mail import send_mail
# from django.conf import settings
# from core.models import HouseUnit
# from tickets.serializers import TicketSerializer
# from django.template.loader import render_to_string 
# from django.core.mail import EmailMultiAlternatives

# @receiver(post_save, sender=Ticket)
# def send_ticket_email(sender, instance, created, **kwargs):
#     if created:
#         unit = HouseUnit.objects.get(pk=instance.unit.pk)
#         landlord_email = unit.house.landlord.email
#         subject = 'New Ticket Created'
#         context = {
#             'unit': unit,
#             'ticket': instance
#         }
#         html_content = render_to_string('email/ticket_created.html', context)
#         text_content = f"New ticket created for {unit.house.name}"
#         msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [landlord_email])
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()

# # send email to tenant when ticket is resolved
# @receiver(post_save, sender=Ticket)
# def send_ticket_resolved_email(sender, instance, created, **kwargs):
#     if instance.status == 'Resolved':
#         tenant_email = instance.unit.tenant.email
#         subject = 'Ticket Resolved'
#         context = {
#             'unit': instance.unit,
#             'ticket': instance
#         }
#         html_content = render_to_string('email/ticket_resolved.html', context)
#         text_content = f"Ticket resolved for {instance.unit.house.name}"
#         msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [tenant_email])
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()