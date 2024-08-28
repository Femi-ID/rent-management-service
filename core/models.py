from django.db import models
import uuid
from users.models import User
from django.conf import settings

class House(models.Model):
    # id = models.UUIDField(default=uuid.uuid4, help_text="To reference the house object when called.")
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='house_details', on_delete=models.CASCADE, limit_choices_to={'user_type': 'LANDLORD'})
    address = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=50, blank=False)
    state = models.CharField(max_length=50, blank=False)
    reg_license = models.CharField(max_length=100, blank=False)
    # image = models.ImageField()
    number_of_units = models.PositiveIntegerField()
    # rent_price = models.PositiveIntegerField()
    # availability = models.BooleanField()

    def __str__(self):
        return f'House address: {self.address[:20]} >> Reg_License: {self.reg_license} >> available: {self.availability}'


class HouseUnit(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  primary_key=True, editable=False, unique=True)
    # id = models.BigAutoField(primary_key=True)
    # unit_image = models.ImageField(upload_to='files/unit_images/', null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="units", null=True, blank=True)
    unit_number = models.CharField(max_length=10, unique=True)
    unit_type = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    rent_price = models.PositiveIntegerField(blank=True, null=True) 
    availability = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.unit_number} - {self.rent_price}"


class LeaseAgreement(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  primary_key=True, editable=False, unique=True)
    house_unit  = models.ForeignKey(HouseUnit, on_delete=models.CASCADE, related_name="lease_agreements")
    document = models.FileField(upload_to="files/lease_agreements/")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Lease Agreement for {self.house_unit}"

    