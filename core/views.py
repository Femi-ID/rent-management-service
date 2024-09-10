from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions
from .models import House, HouseUnit, LeaseAgreement
from .serializer import HouseSerializer, HouseUnitSerializer, LeaseAgreementSerializer
from rest_framework.response import Response 


# create a House
class RegisterHouseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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
        
        existing_house = House.objects.filter(reg_license=request.data['reg_license']).exists()
        if existing_house:
            return Response({
                'msg': 'House with specified details already exists',
                'isSuccess': False
            }, status=400)
        
        serializer = HouseSerializer(data=request.data, context={'owner': request.user})
        if serializer.is_valid():
            house = serializer.save()
            return Response({
                "msg": "House added successfully",
                "uuid": house.pk,
                "owner": house.owner.pk,
                "data": serializer.data,
                'isSuccess': True
            }, status=201)
        return Response(serializer.errors, status=400)

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
            # owner_data = {
            #     "id": house.owner.pk,
            #     "username": house.owner.username,
            # }
            house_data = {
                "id": house.pk,
                "owner": house.owner.pk,
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
            "uuid": house.pk,
            "owner": house.owner.pk,
            "data": serializer.data,
            "isSuccess": True
        }, status=200)
 

# -------------------------THE BEGINNING OF UNITS CLASSES --------------------#
# Register a Unit
class RegisterUnitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        
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
        
        house = None
        if pk:
            try:
                house = House.objects.select_related('owner').get(pk=pk)
          
            except House.DoesNotExist:
                return Response({
                    'msg': 'House not found',
                    'isSuccess': False
                }, status=404)

        existing_unit = HouseUnit.objects.filter(unit_number=request.data['unit_number']).exists()
        
        if existing_unit:
            return Response({
                'msg': 'Unit with specified unit number already exists',
                'isSuccess': False
            }, status=400)

        serializer = HouseUnitSerializer(data=request.data, context={'house': house})
        if serializer.is_valid():
            unit = serializer.save()
            return Response({
                "msg": "Unit added successfully",
                "uuid": unit.pk,
                "data": serializer.data, 
                'isSuccess': True   
            }, status=201)
        return Response(serializer.errors, status=400)

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
            "id": unit.pk,
            "house": unit.house.pk,
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
                "id": unit.pk,
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