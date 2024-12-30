from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from users.models import OnboardUser
from .models import House, HouseUnit
import redis, json
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from adrf.decorators import api_view as adrf_api_view
from .serializer import HouseSerializer, HouseUnitSerializer
from datetime import timedelta
# from celery import shared_task
# import array as arr

redis_client = redis.Redis(
  host=settings.REDIS_CLIENT_HOST,
  port=settings.REDIS_PORT,
  password=settings.REDIS_PASSWORD)

@receiver(pre_delete, sender=House)
def delete_landlord_house_list(sender, instance, **kwargs):
    if instance:
        print('house owner::', instance.owner.email, 'id', instance.id)
        house_id=str(instance.id)
        owner = instance.owner.email
        owner_id=instance.owner.id
        address=instance.address
        city=instance.city
        state=instance.state
        no_of_units=instance.number_of_units
        reg_license=instance.reg_license

        update_redis_landlord_house_list(house_id=house_id, owner=owner, owner_id=owner_id, delete=True)
    

@receiver(post_save, sender=House)
def create_landlord_house_list(sender, instance, created, **kwargs):
    if created:
        print('house owner::', instance.owner.email, 'id', instance.id)
        house_id=instance.id
        owner = instance.owner.email
        owner_id=instance.owner.id
        address=instance.address
        city=instance.city
        state=instance.state
        no_of_units=instance.number_of_units
        reg_license=instance.reg_license

        update_redis_landlord_house_list(user_id=instance.owner, house_id=house_id, owner=owner, owner_id=owner_id, address=address, city=city,
                                         state=state, no_of_units=no_of_units, reg_license=reg_license)
    

def update_redis_landlord_house_list(user_id=None, house_id=None, owner=None, owner_id=None, address=None,
                                      city=None, state=None, no_of_units=None, reg_license=None, delete=False):
    db_houses = House.objects.filter(owner=owner_id).prefetch_related('units')
    serializer = HouseSerializer(db_houses, many=True)
    cached_houses = redis_client.get(f'house-list-{owner_id}')
    if cached_houses is None: 
        redis_client.set(f'house-list-{owner_id}', json.dumps(serializer.data))
        redis_client.expire(f'house-list-{owner_id}', timedelta(weeks=2))
        print("data queried from the Database, new redis cache created")

        redis_houses = redis_client.get(f'house-list-{owner_id}')
        redis_jsonified = json.loads(redis_houses)
        print(f"new redis house:: {redis_jsonified}, number of json houses: {redis_jsonified.__len__()}")
    elif delete==True:
        redis_jsonified = json.loads(cached_houses)
        # delete_house = [house[house_id] for house in redis_jsonified]
        # for house_to_delete in redis_jsonified:
        #     if house_to_delete["id"] == house_id:
        #         print(f"number of json houses: {redis_jsonified.__len__()}, ", f'deleted house-id: {house_to_delete["id"]}')
        #         redis_jsonified.remove(house_to_delete)
        house_to_delete = next((house for house in redis_jsonified if house["id"] == house_id), None)
        if house_to_delete:
            redis_jsonified.remove(house_to_delete)
        print(f"after DEL command, number of json houses: {redis_jsonified.__len__()}")
        redis_client.set(f'house-list-{owner_id}', f'{json.dumps(redis_jsonified)}')
        redis_client.expire(f'house-list-{owner_id}', timedelta(weeks=2))
    else:
        redis_client.delete(f'house-list-{owner_id}')
        redis_client.set(f'house-list-{owner_id}', f'{json.dumps(serializer.data)}')
        redis_client.expire(f'house-list-{owner_id}', timedelta(weeks=2))

        redis_houses = redis_client.get(f'house-list-{owner_id}')
        redis_jsonified = json.loads(redis_houses)
        print(f"number of json houses: {redis_jsonified.__len__()}, \n data loaded from redis cache and updated")


@receiver(post_save, sender=HouseUnit)
def landlord_house_units(sender, instance, created, **kwargs):
    if created:
        house_id = instance.house.id
        owner_id = instance.house.owner.id
        update_landlord_house_units(house_id, owner_id)

@receiver(pre_delete, sender=HouseUnit)
def landlord_house_units(sender, instance, **kwargs):
    if instance:
        house_id = instance.house.id
        owner_id = instance.house.owner.id
        house_unit_id = instance.id
        update_landlord_house_units(house_id, owner_id, house_unit_id=house_unit_id, delete=True)


def update_landlord_house_units(house_id, owner_id, delete=False, house_unit_id=None):
    redis_house_units = redis_client.get(f'house-units-{house_id}-owner-{owner_id}')
    db_house_units = HouseUnit.objects.filter(house__id=house_id, house__owner=owner_id).all()
    serializer = HouseUnitSerializer(db_house_units, many=True)
    if not redis_house_units:
        if db_house_units:
            redis_client.set(f'house-units-{house_id}-{house_id}-owner-{owner_id}', json.dumps(serializer.data))
            redis_client.expire(f'house-units-{house_id}-owner-{owner_id}', timedelta(weeks=2))
            print("data queried from DB")
    elif delete==True and house_unit_id:
        redis_jsonified = json.loads(redis_house_units)
        house_unit_to_delete = next((house_unit for house_unit in redis_jsonified if house_unit["id"] == house_unit_id), None)
        if house_unit_to_delete:
            redis_jsonified.remove(house_unit_to_delete)
        print(f"after DEL command, number of json house units: {redis_jsonified.__len__()}")
        redis_client.set(f'house-units-{house_id}-owner-{owner_id}', f'{json.dumps(redis_jsonified)}')
        redis_client.expire(f'house-units-{house_id}-owner-{owner_id}', timedelta(weeks=2))
    else:
        redis_client.delete(f'house-units-{house_id}-owner-{owner_id}')
        redis_client.set(f'house-units-{house_id}-owner-{owner_id}', json.dumps(serializer.data))
        redis_client.expire(f'house-units-{house_id}-owner-{owner_id}', timedelta(weeks=2))
        print("redis cache updated")


@receiver(post_save, sender=OnboardUser)
def create_email_for_onboarded_user(sender, instance, created, *args, **kwargs):
    if created:
        print('email***', instance.email)
        print('instance >>', instance.house_unit)
        print('sending mail to onboarded user')
        print('sender email', settings.EMAIL_HOST_USER)
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

