from rest_framework import serializers
from .models import Payment, PaymentPlan


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['house_unit', 'amount', 'reference', 'transaction_id', 'status', 'customer_code', 'authorization_code']
