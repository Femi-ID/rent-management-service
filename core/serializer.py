from rest_framework import serializers
from .models import House, HouseUnit


class HouseUnitSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    class Meta:
        model = HouseUnit
        fields = ['id', 'house', 'unit_number', 'unit_type', 'description', 'rent_price', 'availability', 'name_of_owner']

    def get_name_of_owner(self, object):
        return object.house.owner.email
    
    #def get_no_of_house_units(self, object):
     #   return object.units[:]

class HouseSerializer(serializers.ModelSerializer):
    name_of_owner = serializers.SerializerMethodField()
    # TODO: read up how to implement nested modelSerializers
    # house_unit_details = serializers.SerializerMethodField()
    no_of_house_units = serializers.SerializerMethodField()
    house_unit_details = HouseUnitSerializer(many=True, source='units')
    class Meta:
        model = House
        fields = ['id', 'address', 'owner', 'name_of_owner', 'reg_license','number_of_units', 'no_of_house_units','house_unit_details']

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
    
    


