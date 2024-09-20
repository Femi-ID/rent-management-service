from rest_framework import serializers
from .models import House, HouseUnit
from users.models import OnboardUser


class HouseSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    # TODO: read up how to implement nested modelSerializers
    # house_unit_details = serializers.SerializerMethodField()
    no_of_house_units = serializers.SerializerMethodField()
    class Meta:
        model = House
        fields = ['id', 'address', 'owner', 'name_of_owner', 'city','state', 'number_of_units', 'reg_license', 'no_of_house_units']

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
        return str(object.house.owner.email)
    
    # def get_no_of_house_units(self, object):
    #     return object.units[:]


class OnboardUserSerializer(serializers.ModelSerializer):
    # house_address = serializers.SerializerMethodField()
    class Meta:
        model = OnboardUser
        fields = ['email', 'house_unit']

    # def get_house_address(self, object):
    #     return object.house.address