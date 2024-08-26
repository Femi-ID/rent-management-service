from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'reference', 'is_verified', 'created_at')
    list_filter = ('user',  'reference', 'is_verified',) # 'amount',
    search_fields = ('user',)

