from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.Serializer):
    unit = serializers.PrimaryKeyRelatedField(read_only=True)
    subject = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=100)
    status = serializers.CharField(max_length=10)
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField()

    class Meta:
        model = Ticket
        fields = ["subject", "unit", "category", "status"]

    def create(self, validated_data):
        unit = self.context.get('unit')
        validated_data['unit'] = unit
        return Ticket.objects.create(**validated_data)