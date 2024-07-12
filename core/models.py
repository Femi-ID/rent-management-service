from django.db import models
import uuid
from users.models import User
# Create your models here.


class House(models.Model):
    # id = models.UUIDField(default=uuid.uuid4, help_text="To reference the house object when called.")
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    owner = models.ForeignKey(User, related_name='house_details', on_delete=models.CASCADE, limit_choices_to={'user_type': 'LANDLORD'})
    address = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=50, blank=False)
    state = models.CharField(max_length=50, blank=False)
    reg_license = models.CharField(max_length=100, blank=False)
    # image = models.ImageField()
    number_of_units = models.PositiveIntegerField()
    rent_price = models.PositiveIntegerField()
    availability = models.BooleanField()

    def __str__(self):
        return f'House address: {self.address[:20]} >> Reg_License: {self.reg_license} >> available: {self.availability}'




    