from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView

from core import serializer
# from symbol import decorator
from .models import Payment, PaymentPlan, Subscription, PaymentReceipt
from users.models import User
from rest_framework.response import Response
from rest_framework import status, permissions
import requests, json, redis
from django.conf import settings
from .paystack import paystack
from django.http import JsonResponse
from core.models import HouseUnit
from .serializers import PaymentSerializer, PaymentReceiptSerializer, LandlordDashboardSerializer, LandLordDashboardQuerySerializer
from .enums import PaymentStatus
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta

def get_house_unit(house_unit_id):
    house_unit = get_object_or_404(HouseUnit, id=house_unit_id)
    return house_unit

# redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client = redis.Redis(
  host=settings.REDIS_CLIENT_HOST,
  port=settings.REDIS_PORT,
  password=settings.REDIS_PASSWORD)

class AcceptPayment(APIView):
    @swagger_auto_schema(
        operation_description="Initialize a new transaction on Paystack. POST /payments/initialize-payment/{house_unit_id}",
        manual_parameters=[
            openapi.Parameter(
                'house_unit_id',
                openapi.IN_PATH,
                description="The ID of the house unit",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user making payment.'),
            },
        ),
        responses={
            201: openapi.Response(description="Payment initialized"),
            400: openapi.Response(description="Bad request"),
        }
    )
    def post(self, request, house_unit_id):
        if request.user.is_authenticated:
            user = request.user
            house_unit = get_house_unit(house_unit_id=house_unit_id)
            email = request.data.get('email') # may input tenant's email here for onboarding
            # body_unicode = request.body.decode('utf-8')
            # body = json.loads(body_unicode)
            # email = body['email']
            print('email::', email)

            amount = int(house_unit.rent_price*100)
            if not email:
                return Response({"error": "Email must be passed as a request body."},
                                status=status.HTTP_400_BAD_REQUEST)
            initialize_payment = paystack.initialize_payment(email=email, amount=amount)
            if initialize_payment:
                print('initialize payment', initialize_payment)
                reference = initialize_payment['data']['data']['reference']
                authorization_url = initialize_payment['data']['data']['authorization_url']
                payment_obj = Payment.objects.create(user=user, 
                                                     amount=amount, 
                                                     email=email, 
                                                     house_unit=house_unit,
                                                     reference=reference,
                                                     authorization_url=authorization_url
                                                    )
                print('payment obj', payment_obj)
                payment_serializer = PaymentSerializer(payment_obj)
                return Response({'initialize_payment': initialize_payment,
                                 'payment_obj': payment_serializer.data, 
                                 'message' : 'Payment initialized.'})
            return Response({'initialize_payment': initialize_payment,
                             'message' : 'Sorry payment could not be initialized.'})
    

class VerifyPayment(APIView):
    @swagger_auto_schema(
        operation_description="Verify and complete a transaction on Paystack. GET /payments/verify-payment/{house_unit_id}",
        manual_parameters=[
            openapi.Parameter(
                'house_unit_id',
                openapi.IN_PATH,
                description="The ID of the house unit",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'ref',
                openapi.IN_QUERY,
                description="The ref of an initialized payment.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Payment successfully verified."),
            400: openapi.Response(description="Bad request"),
        }
    )
    def get(self, request, house_unit_id):
        """pass reference as a query parameter in the url i.e: 'example.com/?reference=12gwe4323t3y4'"""
        if request.user.is_authenticated:
            # pass reference as a query parameter in the url
            ref = request.GET.get('reference')
            if not ref:
                return Response({"error": "Reference must be passed as a query parameter in the url."},
                                status=status.HTTP_400_BAD_REQUEST)
            verify_transaction = paystack.verify_payment(ref=ref)
            if verify_transaction['response_data']['status'] == False:
                return Response({'response data': verify_transaction},
                                status=status.HTTP_400_BAD_REQUEST)
            transaction_status = verify_transaction['response_data']['data']['status']
            print('transaction status >>>', transaction_status)
            print('verify transaction >>>',verify_transaction)
            
            print('amount...', verify_transaction['response_data']['data']['amount'])
            house_unit = get_house_unit(house_unit_id=house_unit_id)
            print('rent price >>>',house_unit.rent_price)
            payment = Payment.objects.get(reference=ref)
            print('payment::::', payment)

            # store the paystack response in redis cache
            redis_client.set(f'paystack_response_{ref}', json.dumps(verify_transaction['response_data']))
            redis_client.expire(f'paystack_response_{ref}', timedelta(minutes=5))

            if house_unit:
                # try:
                if verify_transaction['response_data']['data']['amount'] == house_unit.rent_price*100:
                    
                    def t_status(transaction_status):
                        match transaction_status:
                            case 'success':
                                payment.transaction_id = verify_transaction['response_data']['data']['id']
                                payment.customer_code = verify_transaction['response_data']['data']['customer']['customer_code']
                                payment.authorization_code = verify_transaction['response_data']['data']['authorization']['authorization_code']
                                payment.is_verified = True
                                payment.status = PaymentStatus.SUCCESS
                                payment.save()
                                payment_serializer = PaymentSerializer(payment)
                                return Response({"message": "Payment confirmed. Thank you.",
                                                    'verify_transaction':verify_transaction,
                                                    'payment_obj': payment_serializer.data},
                                                    status=status.HTTP_200_OK)
                            case 'pending':
                                payment.transaction_id = verify_transaction['response_data']['data']['id'] or None
                                payment.customer_code = verify_transaction['response_data']['data']['customer']['customer_code'] or None
                                payment.save()
                                return Response({"message": "Payment abandoned. Transaction not completed.",
                                                    'verify_transaction':verify_transaction},
                                                    status=status.HTTP_HTTP_200_OK)
                            case 'failed':
                                payment.transaction_id = verify_transaction['response_data']['data']['id'] or None
                                payment.customer_code = verify_transaction['response_data']['data']['customer']['customer_code'] or None
                                payment.save()
                                return Response({"message": "Payment failed. Please try again.",
                                                    'verify_transaction':verify_transaction},
                                                    status=status.HTTP_200_OK)
                            case 'abandoned':
                                payment.transaction_id = verify_transaction['response_data']['data']['id'] or None
                                payment.customer_code = verify_transaction['response_data']['data']['customer']['customer_code'] or None
                                print('transaction_id::', payment.transaction_id)
                                print('customer_code:::', payment.customer_code) 
                                payment.save()
                                return Response({"message": "Payment abandoned. Transaction not completed.",
                                                    'verify_transaction':verify_transaction},
                                                    status=status.HTTP_200_OK)
                            case 'reversed':
                                payment.transaction_id = verify_transaction['response_data']['data']['id'] or None
                                payment.customer_code = verify_transaction['response_data']['data']['customer']['customer_code'] or None
                                payment.save()
                                return Response({"message": "Payment was reversed.",
                                                    'verify_transaction':verify_transaction},
                                                    status=status.HTTP_HTTP_200_OK)
                            case _:
                                return Response({"message": "Unable to verify payment.",
                                                    'verify_transaction':verify_transaction},
                                                    status=status.HTTP_400_BAD_REQUEST)
                    t_status = t_status(transaction_status)
                    return t_status
                else:
                    # this else condition will never be triggered because the transaction price is already set to the rent price 
                    return Response({'message': "The amount for the transaction is not equal to the rent price."},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
                # except Exception as e:
                #     return Response({
                #         "success": False,
                #         "message": f'Your payment was not processed: {e}'
                #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # generate receipt for the transaction

                
            
class CreatePlan(APIView):
    @swagger_auto_schema(
        operation_description="Create a payment plan Paystack. POST /payments/create-plan/",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name','interval', 'amount'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the payment plan.'),
                'interval': openapi.Schema(type=openapi.TYPE_STRING, description='Frequency of this plan to charge the customer.'),
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER, description='Amount to charge per transaction for this plan.'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user making payment.'),
                'invoice_limit': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of times the user will be charged when subscribed to this plan.'),
            },
        ),
        responses={
            201: openapi.Response(description="Payment initialized"),
            400: openapi.Response(description="Bad request"),
        }
    )
    
    def post(self, request):
        """The landlord usertype should only be allowed to create a plan."""
        # TODO: Calculate the amount equivalent for the interval selected usings signals
        # TODO: low-priority feature; add the user_type to the jwt payload
        if request.user.is_authenticated and request.user.user_type == 'Landlord':
            user = request.user
            name = request.data.get('name')
            interval = request.data.get('interval') 
            amount = request.data.get('amount')
            amount_int = int(amount)*100
            # print('amount >>', type(amount))
            amount_str = str(amount_int)
            description = request.data.get('description', None)
            invoice_limit = request.data.get('invoice_limit', None) # no of times to charge the customer

            if not name or not interval:
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                status=status.HTTP_400_BAD_REQUEST)

            def plan_interval(interval):
                    match interval:
                        case 'weekly':
                            return Response({"message": "WEEKLY plan created successfully. Thank you.",
                                             'create_plan':create_plan},
                                             status=create_plan['status'])
                        case 'monthly':
                            return Response({"message": "MONTHLY plan created successfully. Thank you.",
                                             'create_plan':create_plan},
                                             status=create_plan['status'])
                        case 'quarterly':
                            return Response({"message": "QUARTERLY plan created successfully. Thank you.",
                                             'create_plan':create_plan},
                                             status=create_plan['status'])
                        case 'biannually':
                            return Response({"message": "BIANNUALLY plan created successfully. Thank you.",
                                             'create_plan':create_plan},
                                             status=create_plan['status'])
                        case 'annually':
                            return Response({"message": "ANNUALLY plan created successfully. Thank you.",
                                             'create_plan':create_plan},
                                             status=status.HTTP_201_CREATED)
                        case _:
                            return Response({"message": "Invalid plan. Please try again.",
                                             'create__plan':create_plan},
                                             status=create_plan['status'])
            try:
                #TODO: The amount should be generated based on the plan_interval
                create_plan = paystack.create_plan(name=name, interval=interval, amount=amount_str)
                print('create_plan >>>', create_plan)
                if create_plan['response_data']['status'] == True:
                    interval = create_plan['response_data']['data']['interval']
                    plan_id = create_plan['response_data']['data']['id']
                    plan_code = create_plan['response_data']['data']['plan_code']
                    print('plan code>> ', plan_code)
                    
                    payment = PaymentPlan.objects.create(owner=user, name=name,
                                                         interval=interval, amount=amount_str,
                                                         description=description, 
                                                         plan_id=plan_id,
                                                         plan_code=plan_code, 
                                                         invoice_limit=invoice_limit)
                    payment.save()
                    print('payment >>', payment)
                interval = plan_interval(interval)
                return interval
            except Exception as e:
                print(e)
                return Response({"success": False,
                                    "message": f'Internal server error, plan could not be created: {e}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

def get_plan(plan_id):
    plan = get_object_or_404(PaymentPlan, plan_id=plan_id)
    return plan
 

class CreateSubscription(APIView):
    @swagger_auto_schema(
        operation_description="Subscribe to plan created by the landlord. POST create-subscription/{plan_id}/",
        manual_parameters=[
            openapi.Parameter(
                'plan_id',
                openapi.IN_PATH,
                description="The ID of the plan the tenant is subscribing to.",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'start_date': openapi.Schema(type=openapi.FORMAT_DATE, description='The date to start charging the user **"tenant"** for this plan.'),
            },
        ),
        responses={
            201: openapi.Response(description="SUBSCRIPTION CREATED SUCCESSFULLy"),
            400: openapi.Response(description="Bad request"),
        }
    )
    def post(self, request, plan_id):
        """Endpoint to create subscription for an available plan. The tenant subscribes to a plan they can afford."""
        if request.user.is_authenticated:   
            customer_email = request.user.email
            plan = get_plan(plan_id)
            start_date = request.data.get('start_date', None) # this should be the landlord on the create endpoint

            if not customer_email or not plan:
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'
                                 }, status=status.HTTP_400_BAD_REQUEST)
            
            # try:
            create_sub = paystack.create_subscription(plan=plan.plan_code, customer=customer_email)
            print('create sub >>>', create_sub)
            if create_sub['response_data']['status'] == True:
                next_payment_date = create_sub['response_data']['data']['next_payment_date']
                sub = Subscription.objects.create(customer=request.user,
                                                plan=plan,
                                                amount=plan.amount,
                                                status='active',
                                                start_date=start_date,
                                                next_payment_date=next_payment_date,
                                                email_token=create_sub['response_data']['data']['email_token'],
                                                subscription_code=create_sub['response_data']['data']['subscription_code']
                                                )
                sub.save()
                return Response({"message": f"Subscription for the plan: {plan.name} created successfully. Thank you.",
                                'create_sub':create_sub},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Customer prolly hasn't done a transaction before hmmm.",
                                'create_sub':create_sub},
                                status=status.HTTP_400_BAD_REQUEST
                                )


class PaymentHistory(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        payment_history = PaymentReceipt.objects.filter(customer=request.user)
        if payment_history:
            serialized_payment_history = PaymentReceiptSerializer(payment_history, many=True)
            return Response({'message': f"Payment history for {user.email}....",
                             "payment_history": serialized_payment_history.data},
                             status=status.HTTP_200_OK)
        elif not payment_history:
            return Response({'message': "No payment history exists."},
                             status=status.HTTP_204_NO_CONTENT)

# A view for the Landlord Dashboard
class LandlordDashBoard(GenericAPIView):

    serializer_class = LandlordDashboardSerializer
   
    def get_grouped_data(self, payments, period_type):
        if period_type == 'daily':
            grouped_data = payments.values('created_at__date').annotate(total_amount=Sum('amount')).order_by('created_at__date')
        elif period_type == 'weekly':
            grouped_data = payments.annotate(week_start=TruncWeek('created_at')).values('week_start').annotate(total_amount=Sum('amount')).order_by('week_start')
        elif period_type == 'monthly':
            grouped_data = payments.annotate(month=TruncMonth('created_at')).values('month').annotate(total_amount=Sum('amount')).order_by('month')
        elif period_type == 'three_months':
        # Grouping by year and month to avoid mixing payments from different months
            grouped_data = payments.annotate(year_month=TruncMonth('created_at')).values('year_month').annotate(total_amount=Sum('amount')).order_by('year_month')
        else:
            grouped_data = []  # Default empty list if no valid grouping
        return grouped_data
     
    @swagger_auto_schema(
            query_serializer=LandLordDashboardQuerySerializer,
            responses={200: LandlordDashboardSerializer, 400: 'Bad Request', 401:'Unauthorized access', 500: 'Internal Server Error'} , # Documenting a 200 OK response
            operation_description="Period types: 'daily', 'weekly', 'monthly', 'three_months'. Use 'custom' with start_date and end_date."
            
        )

    def get(self, request):

        if request.user.is_authenticated and request.user.user_type == 'Landlord':
             serializer = LandLordDashboardQuerySerializer(data=request.query_params)
             serializer.is_valid(raise_exception=True)
             try:
                period_type = serializer.validated_data.get('period_type')  # e.g., 'daily', 'weekly', 'monthly', 'three_months', 'custom'
                start_date = serializer.validated_data.get('start_date')
                end_date = serializer.validated_data.get('end_date')


                today = timezone.now().date()

                # Retrieve values dynamically from settings
                last_week_days = getattr(settings, 'RENT_PERIODS', {}).get('LAST_WEEK_DAYS', 7)
                last_month_days = getattr(settings, 'RENT_PERIODS', {}).get('LAST_MONTH_DAYS', 30)
                last_three_months_days = getattr(settings, 'RENT_PERIODS', {}).get('LAST_THREE_MONTHS_DAYS', 90)

                payments = Payment.objects.all()


                # Determine the current period and previous period dynamically based on `period_type`
                # Handle period_type logic
                if period_type == 'daily':

                    start_date = today
                    start_date = today 

                     # Previous period: payments for yesterday
                    previous_start_date = today - timedelta(days=1)
                    previous_end_date = previous_start_date

                    # Filter payments for today
                    payments = payments.filter(created_at__date=today)
                    previous_period_payments = payments.filter(created_at__date__gte=previous_start_date, created_at__date__lte=previous_end_date)
                     # Group data based on the specified group_by parameter
                    grouped_data = self.get_grouped_data(payments, period_type)



                elif period_type == 'weekly':

                     # Current period: payments for the last 7 days
                    current_start_date = today - timedelta(days=last_week_days)

                    start_date = current_start_date
                    end_date = today



                     # Previous period: payments for the week before (7 days before the current week)
                    previous_start_date = current_start_date - timedelta(days=last_week_days)
                    previous_end_date = current_start_date - timedelta(days=1)

                    # Filter payments for the last 7 days, including today
                    payments = payments.filter(created_at__date__gte=current_start_date, created_at__date__lte=today)
                    previous_period_payments = payments.filter(created_at__date__gte=previous_start_date, created_at__date__lte=previous_end_date)
  # Group data based on the specified group_by parameter
                    grouped_data = self.get_grouped_data(payments, period_type)


                elif period_type == 'monthly':
                     # Current period: payments for the last 30 days
                    current_start_date = today - timedelta(days=last_month_days)

                    start_date = current_start_date
                    end_date = today
                    
                    # Previous period: payments for the 30 days before the current month
                    previous_start_date = current_start_date - timedelta(days=last_month_days)
                    previous_end_date = current_start_date - timedelta(days=1)

                    # Filter payments for the last 30 days, including today
                    payments = payments.filter(created_at__date__gte=current_start_date, created_at__date__lte=today)
                    previous_period_payments = payments.filter(created_at__date__gte=previous_start_date, created_at__date__lte=previous_end_date)
                     # Group data based on the specified group_by parameter
                    grouped_data = self.get_grouped_data(payments, period_type)

                
                elif period_type == 'three_months':

                     # Current period: payments for the last 90 days
                    current_start_date = today - timedelta(days=last_three_months_days)

                    start_date = current_start_date
                    end_date = today
                    
                    # Previous period: payments for the 90 days before the current three months
                    previous_start_date = current_start_date - timedelta(days=last_three_months_days)
                    previous_end_date = current_start_date - timedelta(days=1)

                    # Filter payments for the last 90 days (approximately 3 months), including today
                    payments = payments.filter(created_at__date__gte=current_start_date, created_at__date__lte=today)
                    previous_period_payments = payments.filter(created_at__date__gte=previous_start_date, created_at__date__lte=previous_end_date)
                     # Group data based on the specified group_by parameter
                    grouped_data = self.get_grouped_data(payments, 'monthly')


                elif period_type == 'custom' and start_date and end_date:
                    # Parse custom date range
                    start_date = parse_date(start_date)
                    end_date = parse_date(end_date)
                    period_type = "custom range"


                    if start_date and end_date:
                         
                         delta = end_date - start_date
                         previous_start_date = start_date - delta
                         previous_end_date = start_date -timedelta(days=1)

                    # Filter payments based on the created_at field
                         payments = payments.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

                         previous_period_payments = payments.filter(created_at__date__gte=previous_start_date, created_at__date__lte=previous_end_date
    )
                         # Group data based on the specified group_by parameter
                    grouped_data = self.get_grouped_data(payments, period_type)

                    if not start_date or not end_date:
                        return Response({'message': 'Invalid date range.'}, status=status.HTTP_400_BAD_REQUEST)

                    if end_date < start_date:
                        return Response({'message': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)


                else:
                    return Response({"message": "Invalid period_type or missing date range"}, status=status.HTTP_400_BAD_REQUEST)
                
                maintainance_cost = Ticket.total_maintenance_cost(start_date, end_date)


                total_rent_paid = payments.aggregate(total=Sum('amount'))['total'] or 0

                previous_total_rent = previous_period_payments.aggregate(total=Sum('amount'))['total'] or 0

                # Calculate percentage increase or decrease
                percentage_change = LandlordDashBoard.get_percentage_change(total_rent_paid, previous_total_rent)

                repairs = Ticket.get_resolved_maintenance_tickets_this_month(self)

                repairs_resolved = repairs['repairs']
                total_tickets_maintainance = repairs['total_tickets']

                vacant_units = HouseUnit.objects.filter(availability=True).count()

                house = House.objects.filter(owner=request.user).first()

                if not house:
                    return Response({"message": "No house found for this user."}, status=status.HTTP_404_NOT_FOUND)
                
                number_of_units = house.number_of_units


                response_data = {
                    'total_rent_paid': total_rent_paid,
                    'percentage_change': percentage_change,
                    'period_type': period_type,
                    'maintainance_cost': maintainance_cost,
                    'vacant_units': vacant_units,
                    'launched_units': number_of_units,
                    'repairs_resolved': repairs_resolved,
                    'total_repairs': total_tickets_maintainance,
                    'grouped_data': list(grouped_data) if grouped_data else [],
                }

                serializer = self.get_serializer(response_data)
                return Response(serializer.data, status=status.HTTP_200_OK)


             except Exception as e:
                return Response({'message': 'Error calculating rent activity', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
    
     
    def get_percentage_change(current, previous):
        if previous == 0:
            return 0  # To avoid division by zero
        return ((current - previous) / previous) * 100

