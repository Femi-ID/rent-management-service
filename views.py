# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from .models import Payment
# from .serializers import PaymentSerializer
# from .paystack import Paystack

# class SetupAutopaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):    
#         serializer = PaymentSerializer(data=request.data)
#         # validate the data
#         if serializer.is_valid():
#             # Extract validated data
#             serialized_data = serializer.validated_data

#             # Create payment instance
#             payment = Payment(
#                 tenant=request.user,
#                 amount = serialized_data["amount"],
#                 frequency = serialized_data["frequency"],
#                 email = request.user.email,
#                 authorization_code = serialized_data.get("authorization_code", "")
#             )
#             payment.save()

#             # Integrate with paystack
#             paystack = Paystack()
#             response = paystack.charge_initial_transaction(serialized_data, request.user)

#             if response.status_code == 200:
#                 response_data = response.json()
#                 payment.ref = response_data["data"]["reference"]
#                 payment.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(response.json(), status=response.status_code)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class VerifyPaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, ref):
#         try:
#             payment = Payment.objects.get(ref=ref, tenant=request.user)
#             if payment.verify_payment():
#                 return Response({'detail': 'Payment verified successfully.'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'detail': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
#         except Payment.DoesNotExist:
#             return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
            


from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import PaymentSerializer
from .models import Payment
from .paystack import Paystack
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from core.models import User
from .models import Plan, Subscription
import json
from datetime import timezone
from dateutil.relativedelta import relativedelta


class AutopaymentSetupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            tenant_id = data['tenant_id']
            amount = data['amount']
            frequency = data['frequency']
            # payment_method = data['payment_method']
            plan_id = data['plan_id']

            try:
                tenant = User.objects.get(id=tenant_id)
                plan = Plan.objects.get(id=plan_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid tenant'}, status=400)
            except Plan.DoesNotExist:
                return JsonResponse({'error': 'Invalid plan'}, status=400)

            # Integrate with Paystack
            paystack = Paystack()
            response = paystack.charge_initial_transaction(data, tenant)
            
            if response.status_code == 200:
                response_data = response.json().get(data)
                authorization_code = response_data['authorization']['authorization_code']

                Subscription.objects.create(
                    tenant=tenant,
                    plan=plan,
                    authorization_code=authorization_code,
                    status='active',
                    start_date=timezone.now(),
                    end_date=timezone.now() + relativedelta(months=1) if frequency == 'monthly' else timezone.now() + relativedelta(years=1)
                )
                return JsonResponse({'message': 'Subscription created successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Failed to create initial charge'}, status=response_data.status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def paystack_webhook(request):
    if request.method == "POST":
        event = json.loads(request.body)
        if event['event'] == 'charge.success':
            data = event['data']
            ref = data['reference']
            authorization_code = data['authorization']['authorization_code']
            payment = Payment.objects.get(ref=ref)
            payment.verified = True
            payment.authorization_code = authorization_code
            payment.save()
            return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'error'}, status=400)


class RecurringChargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            payment = Payment.objects.get(tenant=request.user, verified=True)
            paystack = Paystack()
            response = paystack.charge_authorization(payment.authorization_code, payment.email, payment.amount)
            if response['status']:
                return Response({'detail': 'Charge successful.'}, status=status.HTTP_200_OK)
            else:
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'detail': 'No verified payment found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
#             initial_charge_response = self.charge_initial_transaction(serializer.validated_data, request.user)
#             if initial_charge_response.status_code == 200:
#                 response_data = initial_charge_response.json()
#                 if response_data['data']['authorization']['reusable']:
#                     serializer.save(
#                         authorization_code=response_data['data']['authorization']['authorization_code'],
#                         tenant=request.user
#                     )
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response({"error": "Card is not reusable."}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response({"error": "Initial charge failed."}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def charge_initial_transaction(self, autopayment_data, user):
#         url = "https://api.paystack.co/transaction/initialize"
#         headers = {
#             "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }
#         data = {
#             "email": user.email,
#             "amount": int(autopayment_data['amount'] * 100),  # Convert to kobo
#         }
#         response = requests.post(url, headers=headers, json=data)
#         return response

# class PaystackWebhookView(APIView):
#     def post(self, request):
#         event = request.data
#         if event['event'] == 'charge.success':
#             authorization = event['data']['authorization']
#             Autopayment.objects.filter(tenant__email=event['data']['customer']['email']).update(
#                 authorization_code=authorization['authorization_code'],
#                 card_type=authorization['card_type'],
#                 last4=authorization['last4'],
#                 exp_month=authorization['exp_month'],
#                 exp_year=authorization['exp_year'],
#                 bank=authorization['bank'],
#                 reusable=authorization['reusable'],
#             )
#         return Response(status=status.HTTP_200_OK)