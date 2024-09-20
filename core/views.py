from tkinter import ON
from rest_framework.views import APIView
from rest_framework import permissions
from .models import House, HouseUnit, LeaseAgreement
from .serializer import HouseSerializer, HouseUnitSerializer, LeaseAgreementSerializer
from rest_framework.response import Response 
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404, OnboardUserSerializer
from users.models import OnboardUser as OnBoard
from django.db.models import Prefetch
import json
from users.models import User

# create a House  
class CreateHouse(APIView):
    """View to add/create houses. (Only Landlords are allowed to do so.)"""
    def post(self, request):
        user = request.user
        print(user)
        if user.is_authenticated and user.user_type == 'Landlord':
            try:
                address = request.data.get('address', False)
                city = request.data.get('city')
                state = request.data.get('state')
                reg_license = request.data.get('reg_license')
                number_of_units = request.data.get('number_of_units')
                
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
                                    'error': str(e)},)
            
        
    # view a specific house details
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            house = get_object_or_404(House, id=pk)
            serializer = HouseSerializer(house)
            return Response({'message': 'The house details you requested',
                            'house details': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to view house details'},
                            status=status.HTTP_401_UNAUTHORIZED)
    
    # delete a house
    def delete(self, request, pk):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            house = get_object_or_404(House, id=pk)
            house.delete()
            return Response({'message': 'The house has been deleted'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to delete house'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
    # update a house
    def put(self, request, pk):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            house = get_object_or_404(House, id=pk)
            serializer = HouseSerializer(instance=house, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'The house details has been updated',
                                'house details': serializer.data},
                                status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Authentication required to update house details'},
                            status=status.HTTP_401_UNAUTHORIZED)
    
        
            
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
            availability = request.data['availability']
            unit_number = request.POST.get('unit_number', False)
            unit_type = request.POST.get('unit_type', False)
            description = request.POST.get('description', False)
            rent_price = request.POST.get('rent_price', False)
            availability = request.POST.get('availability', False)

            if not (house, unit_number, unit_type, rent_price, availability):
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                status=status.HTTP_400_BAD_REQUEST)
            
            house_unit = HouseUnit.objects.create(house=house, unit_number=unit_number, 
                                                description=description, rent_price=rent_price,
                                                availability=availability)
            serializer = HouseUnitSerializer(house_unit)
            return Response({'message': 'Your house details has been added',
                            'house details': serializer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': 'Your house details could not be added',
                             'error': str(e)},)
        
    # view a specific unit details
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            house_unit = get_object_or_404(HouseUnit, id=pk)
            serializer = HouseUnitSerializer(house_unit)
            return Response({'message': 'The Unit details you requested',
                            'house details': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to view house details'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
    # edit a unit
    def put(self, request, pk):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            house_unit = get_object_or_404(HouseUnit, id=pk)
            serializer = HouseUnitSerializer(instance=house_unit, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'The Unit details has been updated',
                                'house details': serializer.data},
                                status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Authentication required to update Unit details'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
    # delete a unit
    def delete(self, request, pk):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            house_unit = get_object_or_404(HouseUnit, id=pk)
            house_unit.delete()
            return Response({'message': 'The Unit has been deleted'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to delete house'},
                            status=status.HTTP_401_UNAUTHORIZED)
        

class ListUnitsUnderHouse(APIView):
     # view all unit tied to a specific house
    def get(self, request, house_id):
        user = request.user
        if user.is_authenticated:
            house = get_object_or_404(House, id=house_id)
            house_units = HouseUnit.objects.filter(house=house)
            if not house_units:
                return Response({'message':"You currently haven't added any unit to this house"},
                                status=status.HTTP_204_NO_CONTENT)
            
            serializer = HouseUnitSerializer(house_units, many=True)
            return Response({'message': 'The list of units you added',
                            'house details': serializer.data,},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to view house details'},
                            status=status.HTTP_401_UNAUTHORIZED)

from django.core.serializers import serialize
class OnboardUser(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        house_units = HouseUnit.objects.select_related('house').filter(house__owner=request.user) 
        available_units = house_units.filter(availability=True)
        if house_units:
            house_unit_serializer = HouseUnitSerializer(house_units, many=True)
            return Response({'message':'The list of units owned by the current user',
                            'house units': house_unit_serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message':'You have not added a house/house unit yet.'},
                            status=status.HTTP_204_NO_CONTENT)

    def post(self, request, house_unit_id):
        email = request.data.get('email')
        if User.objects.filter(email=email).first():
            return Response({'message': "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        try:
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
    


class LeaseAgreementView(APIView):
    # create a lease agreement
    def post(self, request, pk):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            house_unit = get_object_or_404(HouseUnit, id=pk)
            existing_lease = LeaseAgreement.objects.filter(house_unit=house_unit).exists()
            if existing_lease:
                return Response({
                    'msg': 'Lease for this unit currently exists',
                    'isSuccess': False
                }, status=400)
            
            serializer = LeaseAgreementSerializer(data=request.data, context={'user': user, 'house_unit': house_unit})
            if serializer.is_valid():
                lease = serializer.save()
                return Response({
                    "msg": "Lease agreement created successfully",
                    'isSuccess': True
                    }, status=201) 
            return Response(serializer.errors, status=400)
        
    # delete a lease agreement
    def delete(self, request, pk):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            lease_agreement = get_object_or_404(LeaseAgreement, id=pk)
            lease_agreement.delete()
            return Response({'message': 'The Lease Agreement has been deleted'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to delete Lease Agreement'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
    # view a specific lease agreement details
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            lease_agreement = get_object_or_404(LeaseAgreement, id=pk)
            serializer = LeaseAgreementSerializer(lease_agreement)
            return Response({'message': 'The Lease Agreement details you requested',
                            'Information': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to view Lease Agreement details'},
                            status=status.HTTP_401_UNAUTHORIZED)
        

class ListAgreementsUnderHouse(APIView):
    # view all lease agreements tied to a specific house
    def get(self, request, house_id):
        user = request.user
        if user.is_authenticated:
            house = get_object_or_404(House, id=house_id)
            house_units = HouseUnit.objects.filter(house=house)
            lease_agreements = LeaseAgreement.objects.filter(house_unit__in=house_units)
            if not lease_agreements:
                return Response({'message':"You currently haven't added any lease agreement to this house"},
                                status=status.HTTP_204_NO_CONTENT)
            
            serializer = LeaseAgreementSerializer(lease_agreements, many=True)
            return Response({'message': 'The list of lease agreements you added',
                            'house details': serializer.data,},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Authentication required to view house details'},
                            status=status.HTTP_401_UNAUTHORIZED)
