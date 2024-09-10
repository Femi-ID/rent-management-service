import uuid
from rest_framework import serializers 
from .models import House, HouseUnit, LeaseAgreement
 
    
class HouseSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    # TODO: read up how to implement nested modelSerializers
    # house_unit_details = serializers.SerializerMethodField()
    no_of_house_units = serializers.SerializerMethodField()
    class Meta:
        model = House
        fields = ['id', 'address', 'owner', 'name_of_owner', 'number_of_units', 'reg_license', 'no_of_house_units']
        read_only_fields = ['owner']

    def get_name_of_owner(self, object):
        return object.owner.email

    def get_no_of_house_units(self, object):
        return object.units.count()

    # def get_house_unit_details(self, object):
    #     house_units = object.units
    #     lists = []
    #     for unit in house_units:
    #         lists.append(unit)
    #         return lists
    
    

class HouseUnitSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    # no_of_house_units = serializers.SerializerMethodField()
    class Meta:
        model = HouseUnit
        fields = ['id', 'house', 'unit_number', 'unit_type', 'description', 'rent_price', 'availability', 'name_of_owner']

    def get_name_of_owner(self, object):
        return object.house.owner.email
    
    # def get_no_of_house_units(self, object):
    #     return object.units[:]

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
    

        