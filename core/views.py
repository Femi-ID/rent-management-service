from rest_framework.views import APIView
from rest_framework import permissions
from .models import House, HouseUnit, LeaseAgreement
from .serializer import HouseSerializer, HouseUnitSerializer, LeaseAgreementSerializer
from rest_framework.response import Response 
from rest_framework import status
from django.shortcuts import get_object_or_404


# create a House  
class CreateHouse(APIView):
    """View to add/create houses. (Only Landlords are allowed to do so.)"""
    def post(self, request):
        user = request.user
        print(user)
        if user.is_authenticated and user.user_type == 'Landlord':

            existing_house = House.objects.filter(reg_license=request.data['reg_license']).exists()
            if existing_house:
                return Response({
                    'msg': 'House with specified details already exists',
                    'isSuccess': False
                }, status=400)

            try:
                address = request.data['address']
                city = request.data['city']
                state = request.data['state']
                reg_license = request.data['reg_license']
                number_of_units = request.data['number_of_units']
                
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

# Get the list of all house registered
class HouseListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)
    
        houses = House.objects.filter(owner_id=request.user.pk)
        data = [] 
        for house in houses:
            house_data = {
                "data": HouseSerializer(house).data 
            }
            data.append(house_data)
        return Response({
            "data": data
        }, status=200)

# Delete a House
class DeleteHouseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        if request.user.user_type != 'Landlord':
            return Response({
                'msg': 'User does not have the correct role to register a house.',
                'isSuccess': False
            }, status=403)
        
        try:
            house = House.objects.get(pk=pk)
            house.delete()
            return Response({
                "msg": "Deleted Successfully", 
                "isSuccess": True
            }, status=200)
        except House.DoesNotExist:
            return Response({
                'msg': 'House not found',
                'isSuccess': False
            }, status=404)

# Update House details
class HouseUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        if request.user.user_type != 'Landlord':
            return Response({
                'msg': 'User does not have the correct role to register a house.',
                'isSuccess': False
            }, status=403)
        
        try:
            house = House.objects.get(pk=pk)
        except House.DoesNotExist:
            return Response({
                'msg': 'House not found',
                'isSuccess': False
            }, status=404)
        
        serializer = HouseSerializer(instance=house, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "msg": "Update Successful",
                "data": serializer.data, 
                "isSuccess": True
                }, status=200)
        return Response(serializer.errors, status=400)

# Get a particular House
class HouseDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)
        try:
            house = House.objects.select_related('owner').get(pk=pk)
        except House.DoesNotExist:
            return Response({
                'msg': 'House not found',
                'isSuccess': False
            }, status=404)

        serializer = HouseSerializer(house, many=False)
        return Response({
            "data": serializer.data,
            "isSuccess": True
        }, status=200)
 

# -------------------------THE BEGINNING OF UNITS CLASSES --------------------#
# Register a Unit
class CreateHouseUnit(APIView):
    def post(self, request, house_id):
        user = request.user
        if user.is_authenticated and user.user_type == 'Landlord':
            try:
                
                house = get_object_or_404(House, pk=house_id)
                unit_number = request.POST.get('unit_number', False)
                unit_type = request.POST.get('unit_type', False)
                description = request.POST.get('description', False)
                rent_price = request.POST.get('rent_price', False)
                availability = request.POST.get('availability', False)

                if not (house, unit_number, unit_type, rent_price, availability):
                    return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                
                existing_unit = HouseUnit.objects.filter(unit_number=request.data['unit_number']).exists()
        
                if existing_unit:
                    return Response({
                        'msg': 'Unit with specified unit number already exists',
                        'isSuccess': False
                    }, status=400)
                
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
        
# View a specific Unit
class UnitDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
 
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        try:
            unit = HouseUnit.objects.get(pk=pk)
        except HouseUnit.DoesNotExist:
            return Response({
                'msg': 'Unit not found',
                'isSuccess': False
            }, status=404)

        serializer = HouseUnitSerializer(unit, many=False)
        return Response({
            "data": serializer.data,
            "isSuccess": True
        }, status=200)

# Delete a specific unit
class DeleteUnitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        if request.user.user_type != 'Landlord':
            return Response({
                'msg': 'User does not have the correct role to register a house.',
                'isSuccess': False
            }, status=403) 
        
        try:
            unit = HouseUnit.objects.get(pk=pk)
            unit.delete()
            return Response({
                "msg": "Deleted Successfully",
                "isSuccess": True
            }, status=200)
        except HouseUnit.DoesNotExist:
            return Response({
                'msg': 'Unit not found',
                'isSuccess': False
            }, status=404)

# Edit a specific unit
class UnitUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        if not request.user.is_authenticated:
                return Response({
                    'msg': 'Authentication credentials were not provided.',
                    'isSuccess': False
                    }, status=401)

        if request.user.user_type != 'Landlord':
            return Response({
                'msg': 'User does not have the correct role to register a house.',
                'isSuccess': False
            }, status=403)  # Forbidden
        
        try:
            unit = HouseUnit.objects.get(pk=pk)
        except HouseUnit.DoesNotExist:
            return Response({
                'msg': 'Unit not found',
                'isSuccess': False
            }, status=404)
        
        serializer = HouseUnitSerializer(instance=unit, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "msg": "Update Successful",
                "data": serializer.data, 
                "isSuccess": True
                }, status=200)
        return Response(serializer.errors, status=400)

# Get all units
class UnitListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        units = HouseUnit.objects.filter(house__owner_id=request.user.pk)
        data = []
        for unit in units:
            unit_data = {
                "data": HouseUnitSerializer(unit).data 
            }
            data.append(unit_data)
        return Response({"data": data}, status=200)


# -----------------------LEASE -------------------------------#
# Create lease
class CreateLeaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        if request.user.user_type != 'Landlord':
            return Response({
                'msg': 'User does not have the correct role to register a house.',
                'isSuccess': False
            }, status=403) 
        
        try:
            house_unit = HouseUnit.objects.get(pk=pk)

            existing_lease = LeaseAgreement.objects.filter(house_unit= house_unit).exists()
        
            if existing_lease:
                return Response({
                    'msg': 'Lease for this unit currently exists',
                    'isSuccess': False
                }, status=400)
        except HouseUnit.DoesNotExist:
            return Response({
                "msg": "Unit with provided ID not found",
                'isSuccess': False
            }, status=400)
        
        serializer = LeaseAgreementSerializer(data=request.data, context={'user': request.user, 'house_unit': house_unit})
        if serializer.is_valid(): 
            lease = serializer.save() 
            return Response({
                "msg": "Lease agreement created successfully",
                'isSuccess': True
                }, status=201) 
        return Response(serializer.errors, status=400)
    
# Delete Lease for a unit
class DeleteLeaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        if request.user.user_type != 'Landlord':
            return Response({
                'msg': 'User does not have the correct role to register a house.',
                'isSuccess': False
            }, status=403)
        
        try:
            lease_agreement = LeaseAgreement.objects.get(pk=pk)
            lease_agreement.delete()
            return Response({
                "msg": "Lease Agreement Deleted Successfully",
                "isSuccess": True
            }, status=200)
        except LeaseAgreement.DoesNotExist:
            return Response({
                'msg': 'Lease Agreement not found',
                'isSuccess': False
            }, status=404)
 
# View a lease
class LeaseDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
 
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)
        
        try:
            lease_agreement = LeaseAgreement.objects.get(pk=pk)
        except LeaseAgreement.DoesNotExist:
            return Response({
                'msg': 'Lease Agreement not found',
                'isSuccess': False
            }, status=404)

        serializer = LeaseAgreementSerializer(lease_agreement, many=False)
        return Response({
            "id": lease_agreement.pk,
            "house_unit": lease_agreement.house_unit.pk,
            "data": serializer.data,
            "isSuccess": True
        }, status=200)
    
# View all lease for all unit
class LeaseAgreementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'msg': 'Authentication credentials were not provided.',
                'isSuccess': False
                }, status=401)

        lease_agreements = LeaseAgreement.objects.filter(house_unit__house__owner_id=request.user.pk)
        data = []
        for lease_agreement in lease_agreements:
            unit_data = {
                "id": lease_agreement.house_unit.pk
            }
            lease_agreement_data = {
                "id": lease_agreement.pk, 
                "house_unit_id": unit_data['id'],
                "data": LeaseAgreementSerializer(lease_agreement).data 
            }
            data.append(lease_agreement_data)
        return Response({"data": data}, status=200)