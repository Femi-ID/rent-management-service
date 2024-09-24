from rest_framework import serializers
from .models import Payment, PaymentPlan


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['house_unit', 'amount', 'reference', 'transaction_id', 'status', 'customer_code', 'authorization_code','created_at']

class LandLordDashboardQuerySerializer(serializers.Serializer):
    period_type = serializers.ChoiceField(
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), 
                 ('three_months', 'Three Months'), ('custom', 'Custom')],
        required=True
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, data):
        period_type = data.get('period_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # If period_type is 'custom', start_date and end_date are required
        if period_type == 'custom':
            if not start_date or not end_date:
                raise serializers.ValidationError("start_date and end_date are required for custom period_type")
        else:
            # If not custom, ensure that start_date and end_date are not set
            if start_date or end_date:
                raise serializers.ValidationError("start_date and end_date should only be provided for custom period_type")
        
        return data

class LandlordDashboardSerializer(serializers.Serializer):
    total_rent_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentage_change = serializers.FloatField()
    period_type = serializers.CharField()
    maintainance_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    vacant_units = serializers.IntegerField()
    launched_units = serializers.IntegerField()
    repairs_resolved = serializers.IntegerField()
    total_repairs = serializers.IntegerField()
    grouped_data = serializers.ListField(
        child=serializers.DictField()  # or a nested serializer if needed
    )