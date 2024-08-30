from email.mime import application, base
from django.conf import settings
import requests


class PayStack:
    PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY
    base_url= 'https://api.paystack.co/transaction'
    headers = {'Authorization': f'Bearer {PAYSTACK_SK}',
               'Content_Type': 'application/json',
               }

    def initialize_payment(self, email, amount, **kwargs):
        path = f'/initialize/'
        url = self.base_url + path
        payload= {
        "email": email, 
        "amount": amount,
        "currency": "NGN",
        # "channels": ['card'],
        # "callback_url": 'http://localhost:8000/payments/verify-payment/'
        }
        
        # send post request with the header, json data
        response = requests.post(url, headers=self.headers, data=payload) 
        response_data = response.json()

        return {'status': response.status_code,
                "message": "Authorization URL created", 
                'data': response_data}
# return response_data['status'], response_data['message'],response_data['data']


    def verify_payment(self, ref, *args, **kwargs):
        # will verify the ref with the secret key provided
        path = f'/verify/{ref}'
        url = self.base_url + path

        response = requests.get(url=url, headers=self.headers)
        response_data = response.json()
        print('response_data: ', response_data)

        if response_data['data']['status'] == 'success':
            # also confirm the amount response['amount'] == house_unit.rent_price
            return {'response_data': response_data}
        
        print('response_data: ', response_data)
        return {'response_data': response_data}


    def create_plan(self, name, interval, amount, description=None, invoice_limit=None, **kwargs):
        url = 'https://api.paystack.co/plan/'
        payload={"name": name,
                 "interval":interval,
                 "amount": amount,
                'description': description,
                'invoice_limit': invoice_limit
                }
        
        response = requests.post(url, headers=self.headers, data=payload)
        print('response >>>', response)
        response_data = response.json()
        if response_data['status'] == True:
            return {'status': response.status_code,
                    "message": "Plan created successfully.", 
                    'response_data': response_data}
        else:
            return {'status': response.status_code,
                    "message": "Plan could not be created.", 
                    'response_data': response_data}

    # def list_transactions(self)

    def create_subscription(self, customer, plan, invoice_limit=None):
        url="https://api.paystack.co/subscription"
        payload={
            "customer": customer, 
            "plan": plan,
            "invoice_limit": invoice_limit
            }
        
        response = requests.post(url, headers=self.headers, data=payload)
        response_data = response.json()
        
        return {'status': response.status_code,
                "message": "Subscription created successfully.", 
                'response_data': response_data}


paystack = PayStack()
