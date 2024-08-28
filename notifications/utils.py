from django.core.mail import send_mail

def send_notification(user, subject, message):
    send_mail(
        subject,
        message,
        'process.env.EMAIL_HOST_USER', #change to your email host user
        [user.email],   
        fail_silently=False,
    )
    print('Email sent successfully')