import stat
from tkinter import ON
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.models import HouseUnit, House
from .serializer import HouseSerializer, HouseUnitSerializer, OnboardUserSerializer
from users.models import OnboardUser as OnBoard
import json
from users.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
                serializer = HouseSerializer(data=request.data, owner=request.user)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'New house created.','data': serializer.data},status=status.HTTP_201_CREATED)
                return Response({'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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
            houses = House.objects.filter(owner=owner_id).prefetch_related('units')
            #TODO: Cache this result
            if not houses:
                return Response({'message':"You currently haven't added any house."},
                                status=status.HTTP_204_NO_CONTENT)
            
            serializer = HouseSerializer(houses, many=True)
            return Response({'message': 'The list of houses you added:','house details': serializer.data},status=status.HTTP_200_OK)
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
            house_units = HouseUnit.objects.filter(house__id=house_id, house__owner=owner_id).all()
            if house_units:
                serializer = HouseUnitSerializer(house_units, many=True)
                return Response({'message':'The list of units owned by the current user',
                                 'house units': serializer.data},
                                 status=status.HTTP_200_OK)
            else:
                return Response({'message':"No units for this house."},status=status.HTTP_204_NO_CONTENT)
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
            house = House.objects.filter(id=house_id).select_related('owner').first()
            if house.owner==user:
                serializer = HouseUnitSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    print('serial', serializer.data)
                    return Response({'message': 'Your house units details has been added',
                                    'house details': serializer.data},
                                    status=status.HTTP_201_CREATED)
                return Response({'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'You are not authorized to create a unit for this house.'}, 
                                status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Your house unit could not be added','error': f'{e}'},
                            status=status.HTTP_501_NOT_IMPLEMENTED)


class OnboardUser(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        """This view displays the list of units owned by the current user and their respective houses"""
        house_units = HouseUnit.objects.select_related('house').filter(house__owner=request.user) 
        available_units = house_units.filter(availability=True)
        print('available units', available_units)
        if house_units:
            house_unit_serializer = HouseUnitSerializer(house_units, many=True)
            available_units_serializer = HouseUnitSerializer(available_units, many=True)
            return Response({'message':'The list of units owned by the current user',
                            'house units': house_unit_serializer.data,
                            'available units': available_units_serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message':'You have not added a house/house unit yet.'},
                            status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
            operation_description="This view displays the list of units owned by the current user and their respective houses).",
            manual_parameters=[
                openapi.Parameter(
                'house_unit_id',
                openapi.IN_QUERY,
                description="The ID of the house unit.",
                type=openapi.TYPE_INTEGER,
                required=True
            )
            ],
            request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the new user to be onboarded.'),
            },
        ),
            responses={
                201: openapi.Response(description="Phase 1 of user onboarding done.."),
                400: openapi.Response(description="Bad request."),
                401: openapi.Response(description="You are not authorized to create a unit for this house."),
                500: openapi.Response(description="Internal server error.")
            }
        )
    def post(self, request):
        """On board a new user to a house unit."""
        email = request.data.get('email')
        if User.objects.filter(email=email).first():
            return Response({'message': "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            house_unit_id = request.GET.get('house_unit_id')
            print('unit id', house_unit_id)
            if not house_unit_id:
                return Response({"error": "The house house unit must be passed as a query parameter in the url."},
                                status=status.HTTP_400_BAD_REQUEST)
            house_unit = HouseUnit.objects.filter(id=house_unit_id, house__owner=request.user, availability=True).first()
            old_user = OnBoard.objects.filter(email=email)
            print('house unit', house_unit)
            print('old user', old_user)
            if house_unit and not old_user:
                serializer = OnboardUserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    print('serial', serializer.data)
                    return Response({'message': 'Phase 1 of user onboarding done.','data': serializer.data},
                                    status=status.HTTP_201_CREATED)
                return Response({'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            if not house_unit:
                return Response({'message': 'House unit is currently unavailable.'}, status=status.HTTP_400_BAD_REQUEST)
            elif old_user:
                return Response({'message': "A user with this email has been previously on-boarded."}, status=status.HTTP_400_BAD_REQUEST)
            
        except HouseUnit.DoesNotExist:
            return Response({'message': "House unit does not exist."},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({"status": 500,
                                 "success": False,
                                 "message": e},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TenantDashboard(APIView):
    """This view displays the user's current house-unit information. ONLY FOR TENANTS."""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        """The tenant's mobile view."""
        house_units = HouseUnit.objects.filter(occupant=request.user).select_related('house__owner')
        if house_units:
            serializer = HouseUnitSerializer(house_units, many=True)
            return Response({'message': 'The house unit the current user is renting.','data': serializer.data},
                             status=status.HTTP_200_OK)
        if request.user.user_type == 'Landlord':
            return Response({'message': 'The current user is a LANDLORD'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'The current user is not yet a tenant'}, status=status.HTTP_204_NO_CONTENT)
        




