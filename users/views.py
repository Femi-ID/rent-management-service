from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView

from users.serializers import UserSerializer, UserProfileSerializer
from .models import User
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from django.http import JsonResponse
from core.models import HouseUnit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="This view displays the user's personal information.",
        # manual_parameters=[
        #     openapi.Parameter(
        #         'house_unit_id',
        #         openapi.IN_PATH,
        #         description="The ID of the house unit",
        #         type=openapi.TYPE_STRING,
        #         required=True
        #     )
        # ],
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     required=['email'],
        #     properties={
        #         'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user making payment.'),
        #     },
        # ),
        responses={
            201: openapi.Response(description="User Profile successfully retrieved."),
            400: openapi.Response(description="Bad request"),
        }
    )
    def get(self, request, user_id):
        user = request.user
        user_profile = User.objects.get(id=user_id)
        if user.id == user_profile.id:
            serializer = UserSerializer(user)
            return Response({'User info': serializer.data})
        else:
            return Response({'error': 'User account does not exist.'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, user_id):
        user = request.user
        try:
            user_profile = get_object_or_404(User, id=user_id)
            if user_profile.id == user.id:
                serializer = UserProfileSerializer(instance=user_profile, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    # update_redis_landlord_house_list(owner_id=user.id, house=house)
                    return Response({'message': 'The user profile has been updated', 
                                     'user details': serializer.data},
                                     status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Only the user can change the profile settings.'},
                                 status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'message': 'The user profile could not be added',
                             'error': f'{e}'}, 
                             status=status.HTTP_501_NOT_IMPLEMENTED)


# def update_redis_landlord_house_list(owner_id, house):
#     """Update a user profile in the Redis list for the given user."""
#     try:
#         db_houses = House.objects.filter(owner=owner_id).prefetch_related('units')
#         serializer = HouseUpdateSerializer(db_houses, many=True)
#         cached_houses = redis_client.get(f'house-list-{owner_id}')
#         if cached_houses is None: 
#             redis_client.set(f'house-list-{owner_id}', json.dumps(serializer.data))
#             redis_client.expire(f'house-list-{owner_id}', timedelta(weeks=2))
#         else:
#             redis_jsonified = json.loads(cached_houses)
#             print('redis jsonified', redis_jsonified[0])
#             for redis_house in redis_jsonified:
#                 if redis_house["id"] == house.id:
#             # updated_house = [house[house.id] for house in redis_jsonified]
#                     redis_house["address"] = house.address
#                     redis_house["city"] = house.city  # Update fields as needed
#                     redis_house["state"] = house.state
#                     redis_house['no_of_house_units'] = house.units.count()
#                     break
#             redis_client.set(f'house-list-{owner_id}', f'{json.dumps(serializer.data)}')
#             redis_client.expire(f'house-list-{owner_id}', timedelta(weeks=2))

#             redis_houses = redis_client.get(f'house-list-{owner_id}')
#             redis_jsonified = json.loads(redis_houses)
#             print(f"data loaded from redis cache and updated house with ID {house.id} in Redis for user {owner_id}")
#     except Exception as e:
        # print(f"Error updating house in Redis for user {owner_id}: {e}")
