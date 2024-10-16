from rest_framework import serializers
from .models import Payment, PaymentReceipt


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['house_unit', 'amount', 'reference', 'is_verified', 'transaction_id', 'status', 'customer_code', 'authorization_code']


class PaymentReceiptSerializer(serializers.ModelSerializer):
    house_unit_number = serializers.SerializerMethodField()
    class Meta:
        model = PaymentReceipt
        fields = ['house_unit_number', 'email', 'amount', 'reference', 'status', 'channel', 'bank', 'transaction_id', 'customer_code', 'transaction_date']

    def get_house_unit_number(self, object):
        return object.payment_id.house_unit.unit_number
    
    # def get_house_unit_id(self, object):
    #     return object.payment_id.house_unit.id
    
    
