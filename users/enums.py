from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

class UserType(TextChoices):
        LANDLORD = "Landlord"
        TENANT = "Tenant"


# class HouseAvailability(models.TextChoices):
        