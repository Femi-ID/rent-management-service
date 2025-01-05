import calendar
from datetime import datetime
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
from payments.models import Payment
from payments.enums import PaymentStatus
from core.utils import get_plot
from django.db.models import Sum
import matplotlib.pyplot as plt
import io


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


class LandlordDashboard(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'Landlord':
            current_year = datetime.now().year
            payments = Payment.objects.filter(house_unit__house__owner=user.id, 
                                             is_verified=True, 
                                             status=PaymentStatus.SUCCESS,
                                             created_at__year=current_year).values('amount', 'created_at')
            
            # Initialize data for each month: {1: 0, 2: 0, ..., 12: 0}
            monthly_data = {month: 0 for month in range(1, 13)} 

            # Sum up payments for each month
            for payment in payments:
                payment_date = payment['created_at']
                payment_month = payment_date.month
                print('month', payment_month)
                monthly_data[payment_month] += payment['amount']

            # Prepare data for plotting
            months = [calendar.month_abbr[i] for i in range(1, 13)]
            amounts = [monthly_data[month] for month in range(1, 13)]
            chart = get_plot(months, amounts)
            # print('payments', payments)

            return Response({'message': 'Your dashboard information.',
                             'payments':payments, 
                             'chart':chart},
                            status=status.HTTP_200_OK)
        return Response({'message': 'Authentication required to view landlord dashboard'},
                        status=status.HTTP_401_UNAUTHORIZED)
    

    def post(self, request):
        try:
            # Get query parameters
            filter_type = request.query_params.get('filter_type', 'yearly')  # Options: yearly, quarterly, monthly
            year = int(request.query_params.get('year', datetime.now().year))
            quarter = int(request.query_params.get('quarter', 0))  # 1, 2, 3, or 4
            month = int(request.query_params.get('month', 0))  # 1-12

            # Filter payments for the specified year and conditions
            payments = Payment.objects.filter(
                house_unit__owner=request.user.id,
                is_verified=True,
                status=PaymentStatus.CONFIRMED,
                created_at__year=year,
            )

            data = {}
            x_axis = []  # Labels
            y_axis = []  # Amounts

            if filter_type == 'yearly':
                # Group payments by month
                monthly_data = payments.values_list('created_at__month').annotate(total=Sum('amount'))
                data = {month: 0 for month in range(1, 13)}  # Initialize months
                for month, total in monthly_data:
                    data[month] = total
                x_axis = [calendar.month_abbr[m] for m in data.keys()]
                y_axis = data.values()
                chart = get_plot(x_axis, y_axis)

            elif filter_type == 'quarterly' and quarter in [1, 2, 3, 4]:
                # Group payments by quarter
                months_in_quarter = {
                    1: [1, 2, 3],
                    2: [4, 5, 6],
                    3: [7, 8, 9],
                    4: [10, 11, 12],
                }
                data = {
                    f"Q{q}": payments.filter(created_at__month__in=months).aggregate(total=Sum('amount'))['total'] or 0
                    for q, months in months_in_quarter.items()
                }
                x_axis = data.keys()
                y_axis = data.values()
                chart = get_plot(x_axis, y_axis)

            elif filter_type == 'monthly' and month in range(1, 13):
                # Group payments by day in the month
                daily_data = payments.filter(created_at__month=month).values_list('created_at__day').annotate(total=Sum('amount'))
                data = {day: 0 for day in range(1, calendar.monthrange(year, month)[1] + 1)}  # Initialize days
                for day, total in daily_data:
                    data[day] = total
                x_axis = data.keys()
                y_axis = data.values()
                chart = get_plot(x_axis, y_axis)

            else:
                return Response(
                    {"error": "Invalid filter_type, quarter, or month."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the plot
            # plt.figure(figsize=(10, 6))
            # plt.bar(x_axis, y_axis, color='skyblue')
            # plt.title(f"Payment Graph ({filter_type.capitalize()})")
            # plt.xlabel("Time")
            # plt.ylabel("Amount (₦)")
            # plt.grid(axis='y')

            # # Save the plot to a buffer
            # buffer = io.BytesIO()
            # plt.savefig(buffer, format='png')
            # plt.close()
            # buffer.seek(0)

            # Return the image
            # return Response(
            #     {"message": "Graph generated successfully."},
            #     content_type="image/png",
            #     headers={"Content-Disposition": "attachment; filename=graph.png"},
            # )

            return Response({'message': 'Your dashboard information.',
                             'payments':payments, 
                             'chart':chart},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)