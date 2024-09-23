from rest_framework import serializers
from .models import House, HouseUnit
from users.models import OnboardUser
import json

class HouseSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    # house_unit_details = serializers.SerializerMethodField()
    no_of_house_units = serializers.SerializerMethodField()
    class Meta:
        model = House
        fields = ['id', 'address', 'name_of_owner', 'city','state', 'number_of_units', 'reg_license', 'no_of_house_units']

    def get_name_of_owner(self, object):
        return object.owner.email

    def get_no_of_house_units(self, object):
        return object.units.count()
    
    def __init__(self, *args, **kwargs):
        # Extract the additional 'owner' argument
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        # Ensure the owner is set when creating the house
        validated_data['owner'] = self.owner
        return super().create(validated_data)

    # def get_house_unit_details(self, object):
    #     house_units = object.units
    #     lists = []
    #     for unit in house_units:
    #         lists.append(unit)
    #     json_object = json.dumps(lists, indent=4)
    #     json_obj = json.loads(json_object)
    #     return json_obj
    
    


class HouseUnitSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    house_id = serializers.SerializerMethodField()
    # no_of_house_units = serializers.SerializerMethodField()
    class Meta:
        model = HouseUnit
        fields = ['id', 'house_id', 'unit_number', 'unit_type', 'description', 'rent_price', 'availability', 'name_of_owner']

    def get_name_of_owner(self, object):
        return str(object.house.owner.email)
    
    def get_house_id(self, object):
        return str(object.house.id)
    
    # def get_no_of_house_units(self, object):
    #     return object.units[:]


class OnboardUserSerializer(serializers.ModelSerializer):
    # house_address = serializers.SerializerMethodField()
    class Meta:
        model = OnboardUser
        fields = ['email', 'house_unit']

    # def get_house_address(self, object):
    #     return object.house.address