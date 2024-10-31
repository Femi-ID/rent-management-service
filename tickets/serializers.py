from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(read_only=True)
    subject = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Ticket
        fields = ["subject", "unit", "category", "created_at", "updated_at", "status", "cost", "id"]

    def create(self, validated_data):
        unit = self.context.get('unit')
        validated_data['unit'] = unit
        return Ticket.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.subject = validated_data.get('subject', instance.subject)
        instance.category = validated_data.get('category', instance.category)
        instance.status = validated_data.get('status', instance.status)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.save()
        return instance