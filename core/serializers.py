import uuid
from rest_framework import serializers 
from .models import House, HouseUnit, LeaseAgreement

class HouseSerializer(serializers.ModelSerializer):
    address = serializers.CharField(max_length=255, required=True)
    city = serializers.CharField(max_length=50, required=True)
    state = serializers.CharField(max_length=50, required=True)
    reg_license = serializers.CharField(max_length=100, required=True)
    number_of_units = serializers.IntegerField(default=0)

    class Meta:
        model = House
        fields = ["address", "city", "state", "reg_license", "number_of_units"]

    def create(self, validated_data):
        owner = self.context.get('owner')
        validated_data['owner'] = owner
        house = House.objects.create(**validated_data)
        return house 


class HouseUnitSerializer(serializers.ModelSerializer):
    house = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True) 
    unit_number = serializers.CharField()
    # unit_image = serializers.ImageField()
    unit_type = serializers.CharField() 
    description = serializers.CharField()
    availability = serializers.BooleanField()
    rent_price = serializers.IntegerField()

    class Meta:
        model = HouseUnit
        fields = ["house", "unit_number", "rent_price", "availability", "unit_type", "description"]
    
    def create(self, validated_data):
        house = self.context.get('house')
        validated_data['house'] = house
        unit = HouseUnit.objects.create(**validated_data)
        return unit 


class LeaseAgreementSerializer(serializers.ModelSerializer):
    document = serializers.FileField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)  

    class Meta:
        model = LeaseAgreement
        fields = ["document", 'created_by']
    
    def create(self, validated_data):
        house_unit = self.context.get('house_unit')
        created_by = self.context['user']
        validated_data['house_unit'] = house_unit
        validated_data['created_by'] = created_by
        lease = LeaseAgreement.objects.create(**validated_data)
        return lease 
    

        
