from django.db import models
from core.models import User
from .paystack import Paystack
import secrets

# Create your models here.
# class Payment(models.Model):
#     tenant = models.ForeignKey(User, related_name='payment_details', on_delete=models.CASCADE)
#     amount = models.PositiveIntegerField()
#     frequency = models.CharField(max_length=50)
#     ref = models.CharField(max_length=250, unique=True)
#     authorization_code = models.CharField(max_length=100, null=True, blank=True)
#     verified = models.BooleanField(default=False)
#     date_created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Autopayment for:{self.tenant.email}"
    
#     def save(self, *args, **kwargs):
#         while not self.ref:
#             ref = secrets.token_urlsafe(50)
#             similar_ref_obj = Payment.objects.filter(ref=ref)
#             if not similar_ref_obj:
#                 self.ref = ref
#         super().save(*args, **kwargs)

#     def amount_value(self):
#         return int(self.amount) * 100
    
#     def verify_payment(self):
#         paystack = Paystack()
#         status, result = paystack.verify_payment(self.ref)
#         if status:
#             if result["amount"] / 100 == self.amount:
#                 self.verified = True
#                 self.save()

#         return self.verified

class Plan(models.Model):
    name = models.CharField(max_length=255)
    paystack_plan_id = models.CharField(max_length=255)
    interval = models.CharField(max_length=50)
    amount = models.IntegerField()  # amount in kobo

class Subscription(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    authorization_code = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
