from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import OnboardUser, User
from core.models import HouseUnit
from rest_framework.response import Response


@receiver(post_save, sender=User)
def add_new_user_house_unit(sender, instance, created, *args, **kwargs):
    if created:
        # print('instance >>', instance)
        registered_onboarded_user = OnboardUser.objects.filter(email=instance.email).first()
        print('registered user', registered_onboarded_user)
        if registered_onboarded_user:
            house_unit = HouseUnit.objects.filter(id=registered_onboarded_user.house_unit.id).first()
            house_unit.occupant = instance
            house_unit.availability = False
            house_unit.save()
            print('Newly registered-onboarded user has been added as an occupant to the house unit!')
