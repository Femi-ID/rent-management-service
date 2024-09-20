from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import OnboardUser, User
from core.models import HouseUnit
import redis, json
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings

@receiver(post_save, sender=User)
def add_new_user_house_unit(sender, instance, created, *args, **kwargs):
    if created:
        # print('instance >>', instance)
        registered_onboarded_user = OnboardUser.objects.filter(email=instance.email).first()
        print('reggg', registered_onboarded_user)
        if registered_onboarded_user:
            house_unit = HouseUnit.objects.filter(id=registered_onboarded_user.house_unit.id).first()
            house_unit.occupant = instance
            house_unit.availability = False
            house_unit.save()
            print('Newly registered-onboarded user has been added as an occupant to the house unit!')
