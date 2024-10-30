from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

class TicketStatus(TextChoices):
        OPEN = "Open"
        RESOLVED = "Resolved"
        PROCESSING = "Processing"
        DECLINED = "Declined"



