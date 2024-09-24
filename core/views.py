from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import HouseUnit, House
from .serializer import HouseSerializer, HouseUnitSerializer


class CreateHouse(APIView):
    """View to add/create houses. (Only Landlords are allowed to do so.)"""
    def post(self, request):
        user = request.user
        print(user)
        if user.is_authenticated and user.user_type == 'Landlord':
            try:
                address = request.data.get('address', False)
                city = request.data.get('city', False)
                state = request.data.get('state', False)
                reg_license = request.data.get('reg_license', False)
                number_of_units = request.data.get('number_of_units', False)
                
                if not address or not city or not state or not reg_license:
                    return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                house = House.objects.create(owner=user, address=address, city=city,
                                            state=state, reg_license=reg_license,
                                            number_of_units=number_of_units)
                
                house.save()

                print(house)

                serializer = HouseSerializer(house)
                # use serializers ??
                return Response({'message': 'Your house details has been added',
                                'house details': serializer.data},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': 'Your house details could not be added',
                                    'error': str(e)})


class ListHousesAndUnits(APIView):
    """View to list the house and house_units belonging to the landlord."""
    def get(self, request, owner_id):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            houses = House.objects.filter(owner=owner_id)
            if not houses:
                return Response({'message':"You currently haven't added any house"},
                                status=status.HTTP_204_NO_CONTENT)
            
            serializer = HouseSerializer(houses, many=True)
            # this should'nt work: houses will return a list of object
            for house in houses:
                house_units = HouseUnit.objects.filter(house=house)
                if house_units:
                    pass
            return Response({'message': 'The list of houses you added',
                                'house details': serializer.data},
                                status=status.HTTP_200_OK)
        
        # TODO: remove the no of units field on the House model


class CreateHouseUnit(APIView):
    def post(self, request, house_id):
        try:
            user = request.user
            house = get_object_or_404(House, id=house_id)
            unit_number = request.data.get('unit_number', False)
            unit_type = request.data.get('unit_type', False)
            description = request.data.get('description', False)
            rent_price = request.data.get('rent_price', False)
            availability = request.data.get('availability', False)

            if not (house, unit_number, unit_type, rent_price, availability):
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                status=status.HTTP_400_BAD_REQUEST)
            
            house_unit = HouseUnit.objects.create(house=house, unit_number=unit_number, 
                                                description=description, rent_price=rent_price,
                                                availability=availability)
            
            house_unit.save()
            serializer = HouseUnitSerializer(house_unit)
            return Response({'message': 'Your house details has been added',
                            'house details': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': 'Your house details could not be added',
                             'error': str(e)})


