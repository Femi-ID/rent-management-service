from django.db import models

class PaymentStatus(models.TextChoices):
        ABANDONED = 'abandoned', # The customer has not completed the transaction.
        FAILED = 'failed',
        ONGOING = 'ongoing', # The customer is currently trying to carry out an action to complete the transaction.
        PENDING = 'pending',
        PROCESSING = 'processing', # Same as pending, but for direct debit transactions.
        QUEUED = 'queued',
        REVERSED = 'reversed', # This could mean the transaction was refunded, or a chargeback was successfully logged for this transaction.
        SUCCESS = "success"