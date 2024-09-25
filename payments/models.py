from django.db import models
from django.forms import EmailField
from users.models import User
import secrets
from .paystack import PayStack

from django.utils.translation import gettext_lazy as _
import uuid
from .enums import PaymentStatus
from core.models import HouseUnit

# class Plan(models.Model):
#     name = models.CharField(max_length=255)
#     paystack_plan_id = models.CharField(max_length=255)
#     interval = models.CharField(max_length=50)
#     amount = models.IntegerField()  # amount in kobo

# class Subscription(models.Model): 
#     tenant = models.ForeignKey(User, on_delete=models.CASCADE)
#     plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
#     authorization_code = models.CharField(max_length=255)
#     status = models.CharField(max_length=50)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house_unit = models.ForeignKey(HouseUnit, on_delete=models.CASCADE, related_name='payments')
    email = models.EmailField()
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=100) 
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PaymentStatus, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(blank=True ,null=True, max_length=20)
    customer_code = models.CharField(max_length=20, null=True)
    authorization_code = models.CharField(max_length=20, null=True)
    authorization_url = models.URLField(max_length=70, editable=False, unique=True,
                                        help_text='redirection link for user to make payment.')
    # update the status in the view

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.user} >> amount: {self.amount}, verified: {self.is_verified}'
    

class PaymentReceipt(models.Model):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='receipt')
    customer =models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=PaymentStatus, default=PaymentStatus.ABANDONED)
    channel = models.CharField(max_length=10, blank=True, null=True)
    bank = models.CharField(blank=True, null=True, max_length=50)
    card_type = models.CharField(blank=True, null=True, max_length=50)
    last4_card_digits = models.CharField(max_length=4, blank=True, null=True) 
    transaction_id = models.CharField(blank=True ,null=True, max_length=20)
    customer_code = models.CharField(max_length=20, null=True, blank=True)
    # authorization_code = models.CharField(max_length=20, null=True)
    # subscription_code = models.CharField(max_length=30, null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #TODO: create an image with all these details and store on the cloud (cloudinary)

class PaymentPlan(models.Model):
    """Payment plan for subscriptions"""
    owner =models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_plans') 
    name = models.CharField(max_length=50)
    interval = models.CharField(max_length=50)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=200, blank=True, null=True)
    plan_id = models.IntegerField()
    plan_code = models.CharField(max_length=30)
    invoice_limit = models.IntegerField() # TODO: Check out the validator argument for integer choices else use IntegerField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'Owner: {self.owner}, Plan Name: {self.name}, Plan CODE: {self.plan_code}'


class Subscription(models.Model):
    customer =models.ForeignKey(User, on_delete=models.CASCADE) # customer's email address or code
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='subscriptions')
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=PaymentStatus, default='active')
    start_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField()
    customer_id_or_code = models.CharField(null=True, blank=True,  max_length=30)
    email_token = models.CharField(max_length=30)
    subscription_code = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
