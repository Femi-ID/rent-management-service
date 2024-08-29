from django.db import models
from core.models import HouseUnit

# Create your models here.
class Ticket(models.Model):
    TICKET_CATEGORY = [
        ('MAINT', 'Maintenance'),
        ('UTIL', 'Utility'),
        ('PAY', 'Payment'),
    ]

    TICKET_STATUS = [
        ('RESOLVED', 'Open'),
        ('PROCESSING', 'In Process'),
        ('DECLINED', 'Declined'),
    ]


    subject = models.CharField(max_length=255)
    unit = models.ForeignKey(HouseUnit, on_delete=models.CASCADE) 
    # assign = models.CharField(max_length=50)
    category = models.CharField(max_length=100, choices=TICKET_CATEGORY)
    status = models.CharField(max_length=100, choices=TICKET_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self,):
        return f"Ticket for {self.unit.unit_number}"