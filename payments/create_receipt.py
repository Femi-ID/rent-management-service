# pdf imports
from email.policy import default
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.core.mail import EmailMessage

import redis, json
from rest_framework.response import Response
from rest_framework import status
from PIL import Image, ImageDraw, ImageFont


redis_client = redis.Redis(host='localhost', port=6379, db=0)

def send_email_with_pdf_image_attachment(reference, amount, 
                                         status, channel, 
                                         bank, card_type, 
                                         last4_card_digits, transaction_id,
                                         customer_code, transaction_date):
    paystack_response = redis_client.get(f'paystack_response_{reference}')
    paystack_response_jsonify = json.loads(paystack_response) 

    # CREATE PDF
    buf = io.BytesIO() # create Bytestream buffer
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0) # create a canvas

    # create a text object
    text_obj = c.beginText()
    text_obj.setTextOrigin(inch, inch)
    text_obj.setFont('Helvetica', 14)

    if paystack_response_jsonify['data']['id']: # for status: success, abandoned
        message = [
            "Rent-PadiiTeam",
            "Femi-007",
            f"AMOUNT: {amount}",
            f"STATUS: {status}",
            f"CHANNEL: {channel}",
            f"BANK: {bank}",
            f"CARD TYPE: {card_type}",
            f"LAST 4 CARD DIGITS: **** **** **** {last4_card_digits}",
            f"TRANSACTION ID: {transaction_id}",
            f"CUSTOMER CODE: {customer_code}",
            f"TRANSACTION DATE: {transaction_date}"
        ]

    for line in message:
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.showPage()
    c.save()
    buf.seek(0)
    FileResponse(buf, as_attachment=True, filename='receipt.pdf')

    # CREATE IMAGE RECEIPT
    img_buffer = io.BytesIO()

    # img = Image.new(color, dimension, color-value)
    img = Image.new(mode='RGB', size=(400, 700), color=(255, 255, 255))
    draw = ImageDraw.Draw(img) # to draw/write on the new image

    try:
        font = ImageFont.truetype("timesbd.ttf", 12)
    except IOError:
        font = ImageFont.load_default()  # Fallback to default if font not found

    message_string = ''.join(message)
    print(message_string)

    # draw.text(coordinates, text, rgb values for color, font)
    draw.text((10, 10), message_string, fill=(0, 0, 0), font=font)
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    
# SEND EMAIL
# def send_mail(subject, message, from_email, recipient_list):
    email = EmailMessage(
        subject=f'Transfer {status}. Reference number:{reference}',
        body=f"Your transfer of #{amount} has a status: {status}. View the pdf attachment for more details. Thank you.",
        from_email='technewmann@gmail.com',
        to=['femiidowu28@gmail.com'],
    )
    
    # Attach the document (PDF)
    email.attach('receipt.pdf', buf.getvalue(), 'application/pdf')

    # Attach the image (PNG)
    email.attach('string_data.png', img_buffer.getvalue(), 'image/png')

    # Step 4: Send the email
    email.send(fail_silently=False)
    print('email sent successfully.')
    