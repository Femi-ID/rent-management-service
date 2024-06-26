from django.db import models
from django.utils.translation import gettext_lazy as _

class UserType(models.TextChoices):
        LANDLORD = "Landlord", _("Landlord")
        TENANT = "Tenant", _("Tenant")


# class HouseAvailability(models.TextChoices):
        



