from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from .models import Payment, PaymentPlan
from users.models import User
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from .paystack import paystack
from django.http import JsonResponse
from core.models import HouseUnit
import json
from django.shortcuts import get_object_or_404
# from pypaystack import Plan

# TODO: CREATE AND SAVE PAYMENT INSTANCE FROM THE MODEL
# return JsonResponse(user_list, safe=False)
# TODO: retrieve the generated reference pay['data']['reference']
# TODO: I'm currently unable to create a payment obj with the initialize response

def get_house_unit(house_unit_id):
    house_unit = get_object_or_404(HouseUnit, id=house_unit_id)
    return house_unit

class AcceptPayment(APIView):
    """The first stage of Paystack transaction. This endpoint accepts the email and amount of the user initializing the transaction."""
    # The landlord is only allowed to send the email of the tenant while the amount is gotten from the rent_price of the """
    def post(self, request, house_unit_id):
        if request.user.is_authenticated:
            user = request.user
            house_unit = get_house_unit(house_unit_id=house_unit_id)
            email = request.POST['email']

            initialize_payment = paystack.initialize_payment(email=user.email, amount=house_unit.rent_price)
            if initialize_payment:
                # initial_payment_json = initial_payment.json()
                reference=json.dumps(initialize_payment["data"])
                print('initialize payment', initialize_payment)
                print('reference::: ', reference)
                payment_obj = Payment.objects.create(user=user, amount=house_unit.rent_price, 
                                                    reference=initialize_payment['data']['data']['reference'],
                                                    house_unit=house_unit)
                return Response({'initialize_payment': initialize_payment, 
                                'payment_obj': payment_obj, 
                                'message' : 'Payment initialized.'})
            return Response({'initialize_payment': initialize_payment,
                                'message' : 'Payment could not be initialized.'})
    

class VerifyPayment(APIView):
    def get(self, request, house_unit_id):
        if request.user.is_authenticated:
            ref = request.GET.get('reference')
            verify_transaction = paystack.verify_payment(ref=ref)
            transaction_status = verify_transaction['response_data']['data']['status']
            print(ref)
            print('transaction status >>>', transaction_status)
            print('verify transaction >>>',verify_transaction)
            house_unit = get_house_unit(house_unit_id=house_unit_id)
            payment = Payment.objects.get(reference=ref)

            if house_unit:
                try:
                    if verify_transaction['response_data']['data']['amount'] == house_unit.rent_price:
                        if transaction_status == 'success':
                            payment.transaction_id = verify_transaction['response_data']['data']['id']
                            payment.save()
                            return Response({"message": "Payment confirmed. Thank you.",
                                             'verify_transaction':verify_transaction},
                                             status=status.HTTP_200_OK)
                        elif transaction_status == 'failed':
                            return Response({"message": "Payment failed. Please try again.",
                                             'verify_transaction':verify_transaction},
                                            status=status.HTTP_400_BAD_REQUEST)
                        elif transaction_status == 'reversed':
                            return Response({"message": "Payment was reversed.",
                                             'verify_transaction':verify_transaction},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # this else condition will never be triggered because the transaction price is already set to the rent price 
                        return Response({'message': "The amount for the transaction is not equal to the rent price."},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)
                except Exception as e:
                    return Response({
                        "success": False,
                        "message": f'Internal server error, payment was not processed: {e}'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            
class CreatePlan(APIView):
    """The landlord usertype should only be allowed to create a plan."""
    def post(self, request):
        # TODO: Calculate the amount equivalent for the interval selected usings signals
        # TODO: low-priority feature; add the user_type to the jwt payload
        if request.user.is_authenticated and request.user.user_type == 'Landlord':
            user = request.user
            print('user >>>>', user)
            name = request.POST['name']
            interval = request.POST['interval']
            amount = request.POST['amount'] 
            description = request.POST.get('description', None)
            invoice_limit = request.POST.get('invoice_limit', None)

            if not name or not interval:
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'},
                                status=status.HTTP_400_BAD_REQUEST)

            def plan_interval(interval):
                    match interval:
                        case 'weekly':
                            return Response({"message": "WEEKLY plan created successfully. Thank you.",
                                                'create_plan':create_plan},
                                                status=status.HTTP_201_CREATED)
                        case 'monthly':
                            return Response({"message": "MONTHLY plan created successfully. Thank you.",
                                                'create_plan':create_plan},
                                                status=status.HTTP_201_CREATED)
                        case 'quarterly':
                            return Response({"message": "QUARTERLY plan created successfully. Thank you.",
                                                'create_plan':create_plan},
                                                status=status.HTTP_201_CREATED)
                        case 'biannually':
                            return Response({"message": "BIANNUALLY plan created successfully. Thank you.",
                                                'create_plan':create_plan},
                                                status=status.HTTP_201_CREATED)
                        case 'annually':
                            return Response({"message": "ANNUALLY plan created successfully. Thank you.",
                                                'create_plan':create_plan},
                                                status=status.HTTP_201_CREATED)
                        case _:
                            return Response({"message": "Invalid plan. Please try again.",
                                                'create__plan':create_plan},
                                            status=status.HTTP_400_BAD_REQUEST)
            try:
                create_plan = paystack.create_plan(name=name, interval=interval, amount=amount)
                print('create_plan >>>', create_plan)
                if create_plan['response_data']['status'] == True:
                    interval = create_plan['response_data']['data']['interval']
                    plan_id = create_plan['response_data']['data']['id']
                    plan_code = create_plan['response_data']['data']['plan_code']
                    print('plan code>> ', plan_code)
                    
                    payment = PaymentPlan.objects.create(owner=user, name=name,
                                               interval=interval, amount=amount,
                                               description=description, plan_id=plan_id,
                                               plan_code=plan_code, invoice_limit=invoice_limit)
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
    """"Endpoint to create subscription for an available plan. The tenant subscribes to a plan he/she can afford."""
    def post(self, request, plan_id):
        if request.user.is_authenticated:   
            customer = request.user.email
            plan = get_plan(plan_id)

            if not customer or not plan:
                return Response({'message': 'Request body incomplete, ensure all required fields are complete!'
                                 }, status=status.HTTP_400_BAD_REQUEST)
            
            # try:
            create_sub = paystack.create_subscription(plan=plan.plan_code, customer=customer)
            print('create sub >>>', create_sub)
            # if create_sub['response_data']['data']['status'] == 'active':
            if create_sub['response_data']['status'] == True:
                return Response({"message": f"Subscription for the plan: {plan.name} created successfully. Thank you.",
                                 'create_sub':create_sub},
                                 status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Customer prolly hasn't done a transaction before hmmm.",
                                 'create_sub':create_sub},
                                 status=status.HTTP_400_BAD_REQUEST
                                 )


  
