from django.conf import settings
import requests

class Paystack:
    PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY
    base_url = "https://api.paystack.co/"
    headers = {
            "Authorization": f"Bearer {PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
    
    def create_paystack_plan(self, name, amount, interval):
        path = 'plan'
        headers = {
            'Authorization': 'Bearer YOUR_PAYSTACK_SECRET_KEY',
            'Content-Type': 'application/json',
        }
        data = {
            'name': name,
            'amount': amount,
            'interval': interval,
            'currency': 'NGN'
        }
        url = self.base + path
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def charge_initial_transaction(self, autopayment_data, user):
        path = f"transaction/initialize"
        data = {
            "email": user.email,
            "amount": int(autopayment_data['amount'] * 100),  # Convert to kobo
        }
        url = self.base_url + self.path
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def verify_payment(self, ref):
        path = f"transaction/verify/{ref}"
        url = self.base_url + path
        response = requests.get(url, headers=self.headers)
        response_data = response.json()
        if response.status_code == 200:
            return response_data["status"], response_data["data"]
        
        return response_data["status"], response_data["message"]
    
    def charge_authorization(self, authorization_code, email, amount):
        path = "transaction/charge_authorization"
        data = {
            "authorization_code": authorization_code,
            "email": email,
            "amount": amount * 100  # Convert to kobo
        }
        url = self.base_url + path
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
