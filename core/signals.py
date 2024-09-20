from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import OnboardUser
import redis, json
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings


@receiver(post_save, sender=OnboardUser)
def create_email_for_onboarded_user(sender, instance, created, *args, **kwargs):
    if created:
        print('email***', instance.email)
        print('instance >>', instance.house_unit)
        print('sending mail to onboarded user')
        email = EmailMessage(
            subject = 'RENT-PADII ONBOARDING PHASE ',
            body = f'''\t\tGood day, your ONBOARDING PHASE process has begun.
            Please register a new account with this email address: {instance.email} to complete your account setup.
            Thank you.
            You are receiving this mail because you have being on-boarded by your landlord, if this is not the case please dismiss this email.
            \n\t\tThe RENT PADII Team''',
            from_email = f'{settings.EMAIL_HOST_USER}',
            to = [f'{instance.email}'],
        )
        

        email.send(fail_silently=False)
        print(f'email successfully sent to {instance.email}')

