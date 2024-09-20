from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete # pre_delete: user deletes a payment record that hasn't been completed
from payments.models import Payment, PaymentReceipt
import redis, json
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail

# pdf imports
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.core.mail import EmailMessage
from .create_receipt import send_email_with_pdf_image_attachment


redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_payment_receipt(receipt_reference):
    try:
        receipt = PaymentReceipt.objects.get(reference=receipt_reference)
        return receipt
    except PaymentReceipt.DoesNotExist:
        return Response({'error': 'No existing payment payment receipt for this payment:{receipt_reference}',
                         "status": 404},
                        status= status.HTTP_404_NOT_FOUND)
    

@receiver(post_save, sender=Payment)
def create_receipt_for_payment(sender, instance, created, *args, **kwargs):
    if created: 
        print('New receipt created for new payment.')
        receipt_obj = PaymentReceipt.objects.create(
            payment_id=instance,
            customer=instance.user,
            email=instance.email,
            amount=int(instance.amount/100),
            reference=instance.reference,
            status=instance.status
        )
        receipt_obj.save()
        print('receipt:::', receipt_obj)
    else: 
        # payment object-instance is being updated
        print('Receipt is being updated not created.')
        reference = instance.reference
        receipt = get_payment_receipt(reference)
        print('receipt>>>>', receipt)
        paystack_response = redis_client.get(f'paystack_response_{reference}')
        paystack_response_jsonify = json.loads(paystack_response)

        if paystack_response_jsonify['status']==True and instance.transaction_id:
            receipt.status=paystack_response_jsonify['data']['status'] or None
            receipt.channel=paystack_response_jsonify['data']['channel'] or ''
            receipt.transaction_id=paystack_response_jsonify['data']['id'] or None
            receipt.customer_code=paystack_response_jsonify['data']['customer']['customer_code']
            receipt.transaction_date=paystack_response_jsonify['data']['transaction_date']
            print('receipt status', receipt.status)
        
            if paystack_response_jsonify['data']['status'] == 'success' or 'failed':
                # receipt.channel=paystack_response_jsonify['data']['channel'] or ''
                receipt.bank=paystack_response_jsonify['data']['authorization']['bank'] or ''
                receipt.card_type=paystack_response_jsonify['data']['authorization']['card_type'] or None
                receipt.last4_card_digits=paystack_response_jsonify['data']['authorization']['last4'] or None
                # receipt.transaction_id=paystack_response_jsonify['data']['id'] or None
                # receipt.customer_code=paystack_response_jsonify['data']['customer']['customer_code']
                # receipt.transaction_date=paystack_response_jsonify['data']['transaction_date']
                # print(f'receipt created. Reference: {reference}, Status: {receipt.status}')
                # receipt.save()
            print(f'receipt created. Reference: {reference}, Status: {receipt.status}')
            receipt.save()
        else:
            print('No transaction has occured for this payment. It has only been initialized.')
        
    send_email_with_pdf_image_attachment(reference=reference, 
                                         amount=int(instance.amount/100), 
                                         status=receipt.status, 
                                         channel=receipt.channel, 
                                         bank=receipt.bank, 
                                         card_type=receipt.card_type, 
                                         last4_card_digits=receipt.last4_card_digits, 
                                         transaction_id=receipt.transaction_id,
                                         customer_code=receipt.customer_code, 
                                         transaction_date=receipt.transaction_date)

            # if paystack_response_jsonify['data']['status'] == 'abandoned':
            #     receipt.channel=paystack_response_jsonify['data']['channel'] or ''
            #     receipt.transaction_id=paystack_response_jsonify['data']['id'] or None
            #     receipt.customer_code=paystack_response_jsonify['data']['customer']['customer_code']
            #     receipt.transaction_date=paystack_response_jsonify['data']['transaction_date']
            #     print(f'receipt created. Reference: {reference}, Status: {receipt.status}')
            #     receipt.save()

            # if paystack_response_jsonify['data']['status'] == 'failed':
            #     receipt.channel=paystack_response_jsonify['data']['channel'] or ''
            #     receipt.bank=paystack_response_jsonify['data']['authorization']['bank'] or ''
            #     receipt.card_type=paystack_response_jsonify['data']['authorization']['card_type'] or None
            #     receipt.last4_card_digits=paystack_response_jsonify['data']['authorization']['last4'] or None
            #     receipt.transaction_id=paystack_response_jsonify['data']['id'] or None
            #     receipt.customer_code=paystack_response_jsonify['data']['customer']['customer_code']
            #     receipt.transaction_date=paystack_response_jsonify['data']['transaction_date']
            #     print(f'receipt created. Reference: {reference}, Status: {receipt.status}')
            #     receipt.save()
            

    
