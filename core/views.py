import stat
from tkinter import ON, W
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.models import HouseUnit, House
from .serializer import HouseSerializer, HouseUnitSerializer, OnboardUserSerializer
from users.models import OnboardUser as OnBoard
import json, redis
from users.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta
from django.conf import settings


# redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client = redis.Redis(
  host=settings.REDIS_CLIENT_HOST,
  port=settings.REDIS_PORT,
  password=settings.REDIS_PASSWORD)

class CreateHouse(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Add a house to the application. POST /houses/create-house/",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['address', 'city', 'state', 'reg_license'],
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Address of the house.'),
                'city': openapi.Schema(type=openapi.TYPE_STRING, description='City of the house location.'),
                'state': openapi.Schema(type=openapi.TYPE_STRING, description='State of the house location.'),
                'reg_license': openapi.Schema(type=openapi.TYPE_STRING, description='Registration license of the house.'),
            },
        ),
        responses={
            201: openapi.Response(description="House created"),
            400: openapi.Response(description="Bad request"),
        }
    )
    def post(self, request):
        """View to add/create houses. (Only Landlords are allowed to do so.)"""
        user = request.user
        if user.user_type == 'Landlord':
            try:
                address = request.POST.get('address', False)
                city = request.POST['city']
                state = request.POST['state']
                reg_license = request.POST['reg_license']
                number_of_units = request.POST['number_of_units']
                
                if not address or not city or not state or not reg_license:
                    return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                house = House.objects.create(owner=user, address=address, city=city,
                                            state=state, reg_license=reg_license,
                                            number_of_units=number_of_units)
                serializer = HouseSerializer(house)
                print(house)
                # use serializers ??
                return Response({'message': 'Your house details has been added',
                                'house details': serializer.data},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': 'Your house details could not be added',
                                 'error': f'{e}'}, 
                                 status=status.HTTP_501_NOT_IMPLEMENTED)
        return Response({'message':'Only landlords can create houses.'}, status=status.HTTP_401_UNAUTHORIZED)


class ListHouses(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """View to list the house and number of house_units belonging to the landlord."""
    @swagger_auto_schema(
        operation_description="Lists the houses belonging to the current user(Landlord). GET /houses/list-houses/<str:owner_id>/",
        manual_parameters=[
            openapi.Parameter(
                'owner_id',
                openapi.IN_PATH,
                description="The ID of the current user",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Returned list of houses you added."),
            204: openapi.Response(description="You currently haven't added any house."),
            401: openapi.Response(description="Only landlords can access this view."),
        }
    )
    def get(self, request, owner_id):
        user = request.user
        if user.user_type == 'Landlord':
            houses = redis_client.get(f'house-list-{user.id}')
            if houses is None:
                houses = House.objects.filter(owner=owner_id).prefetch_related('units')
                if not houses:
                    return Response({'message':"You currently haven't added any house."}, status=status.HTTP_204_NO_CONTENT)
            
                serializer = HouseSerializer(houses, many=True)
                redis_client.set(f'house-list-{user.id}', json.dumps(serializer.data))
                redis_client.expire(f'house-list-{user.id}', timedelta(hours=2))
                print("data loaded from DB")
                return Response({'message': 'The list of houses you added:','house details': serializer.data},status=status.HTTP_200_OK)
            else:
                json_houses = json.loads(houses)
                print("data loaded from redis cache")
                return Response({'message': 'The list of houses from redis cache:','house details': json_houses},status=status.HTTP_200_OK)
        return Response({'message':"Only landlords can access this view."},status=status.HTTP_401_UNAUTHORIZED)


class ListHouseUnits(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """View to list the house and number of house_units belonging to the landlord."""
    @swagger_auto_schema(
        operation_description="Lists the house units belonging to the current user(Landlord). GET /houses/list-houses/<str:owner_id>/",
        manual_parameters=[
            openapi.Parameter(
                'owner_id',
                openapi.IN_PATH,
                description="The ID of the current user",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'house_id',
                openapi.IN_PATH,
                description="The ID of the house",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Returned list of houses you added."),
            204: openapi.Response(description="No units for this house."),
            401: openapi.Response(description="Only landlords can access this view."),
        }
    )
    def get(self, request, owner_id, house_id):
        user = request.user
        if user.user_type == 'Landlord':
            house_units = redis_client.get(f'house-units-{house_id}')
            if not house_units:
                house_units = HouseUnit.objects.filter(house__id=house_id, house__owner=owner_id).all()
                if house_units:
                    serializer = HouseUnitSerializer(house_units, many=True)
                    redis_client.set(f'house-units-{house_id}', json.dumps(serializer.data))
                    redis_client.expire(f'house-units-{house_id}', timedelta(hours=2))
                    print("data loaded from DB")
                    return Response({'message':'The list of units owned by the current user',
                                    'house units': serializer.data},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'message':"No units for this house."},status=status.HTTP_204_NO_CONTENT)
            else:
                json_house_units = json.loads(house_units)
                print("data loaded from redis cache")
                return Response({'message': 'List of house-units from redis cache:','house details': json_house_units},status=status.HTTP_200_OK)
        return Response({'message':"Only landlords can access this view."},status=status.HTTP_401_UNAUTHORIZED)


class CreateHouseUnit(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
            operation_description="Create house units for a house. The current user(Landlord). GET /houses/list-houses/<str:owner_id>/",
            manual_parameters=[
                openapi.Parameter(
                    'house_id',
                    openapi.IN_PATH,
                    description="The ID of the house",
                    type=openapi.TYPE_STRING,
                    required=True
                )
            ],
            request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['house', 'unit_number', 'unit_type', 'rent_price', 'availability'],
            properties={
                'house': openapi.Schema(type=openapi.TYPE_STRING, description='House ID.'),
                'unit_number': openapi.Schema(type=openapi.TYPE_STRING, description='This is self-descriptive.'),
                'unit_type': openapi.Schema(type=openapi.TYPE_STRING, description='Example: flat, duplex, self-contain....'),
                'rent_price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Amount for the rent.'),
                'availability': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Boolean:: True/False.'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='State of the house location.')
            }
            ),
            responses={
                201: openapi.Response(description="Your house units details has been added."),
                400: openapi.Response(description="Bad request, check that the data you sent is of the correct type and complete."),
                401: openapi.Response(description="You are not authorized to create a unit for this house."),
            }
        )
    def post(self, request, house_id):
        """View to create house unit for a house. Only the house owner (landlord) can create units."""
        try:
            user = request.user
            house = get_object_or_404(House, id=house_id)
            unit_number = request.POST.get('unit_number', False)
            unit_type = request.POST.get('unit_type', False)
            description = request.POST.get('description', False)
            rent_price = request.POST.get('rent_price', False)
            availability = request.POST.get('availability', False)

            if not (house, unit_number, unit_type, rent_price, availability):
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                status=status.HTTP_400_BAD_REQUEST)
            
            house_unit = HouseUnit.objects.create(house=house_id, unit_number=unit_number, 
                                                description=description, rent_price=rent_price,
                                                availability=availability)
            serializer = HouseUnitSerializer(house_unit)
            return Response({'message': 'Your house details has been added',
                            'house details': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': 'Your house details could not be added',
                             'error': {e}})


