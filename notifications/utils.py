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


# send mail upon payment by tenant to landlord
# def send_email_upon_payment(user, house_unit):
#     send_mail(
#         'Rent Payment Notification',
#         f'Your tenant: {user.email} has paid their rent for {house_unit.unit_number}.',
#         'process.env.EMAIL_HOST_USER', #change to your email host user
#         [house_unit.house.owner.email],   
#         fail_silently=False,
#     ) 


# # send mail to landlord when a tenants makes a ticket
# def send_ticket_notification_to_landlord(user, house_unit):
#     send_mail(
#         'New Ticket Notification',
#         f'Your tenant: {user.email} has made a ticket for {house_unit.unit_number}.',
#         [user.email], #change to your email host user
#         [house_unit.house.owner.email],   
#         fail_silently=False,
#     )


# # send an email to the tenant when a ticket has been resolved
# def send_ticket_notification_to_tenant(user, house_unit):
#     send_mail(
#         'New Ticket Notification',
#         f'Your Lanlord: {house_unit.house.owner.email} has resolved the ticket for {house_unit.unit_number}.',
#         'process.env.EMAIL_HOST_USER', #change to your email host user
#         [user.email],   
#         fail_silently=False,
#     )
