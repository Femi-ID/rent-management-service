from django.db import models
from core.models import HouseUnit
from django.db.models import Sum
from django.utils import timezone

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
    #assigning cost to the model
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self,):
        return f"Ticket for {self.unit.unit_number}"
    

    #adding class methods
    @classmethod
    def total_maintenance_cost(cls, start_date, end_date):
        return cls.objects.filter(
            category='MAINT',
            created_at__range=(start_date, end_date)
        ).aggregate(total_cost=Sum('cost'))['total_cost'] or 0

    def get_resolved_maintenance_tickets_this_month(self):
        # Get the first and last day of the current month
        today = timezone.now()
        first_day_of_month = today.replace(day=1)
        next_month = first_day_of_month.replace(month=today.month + 1) if today.month < 12 else first_day_of_month.replace(year=today.year + 1, month=1)
        
        # Calculate total resolved tickets and total tickets for this month
        repairs = Ticket.objects.filter(
            category='MAINT',
            status='RESOLVED',
            created_at__gte=first_day_of_month,
            created_at__lt=next_month
        ).count()

        total_tickets = Ticket.objects.filter(
            category='MAINT',
            created_at__gte=first_day_of_month,
            created_at__lt=next_month
        ).count()

        return {'repairs':repairs,
                'total_tickets':total_tickets
                }