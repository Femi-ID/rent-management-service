# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import authentication, permissions, status
# from core.models import HouseUnit
# from tickets.models import Ticket
# from tickets.serializers import TicketSerializer
# from notifications.utils import send_ticket_notification_to_landlord, send_ticket_notification_to_tenant

# # Create a ticket
# class CreateTickets(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk):
#         if request.user.user_type != 'Tenant':
#             return Response({ 
#                 'msg': 'User does not have the correct role to create a ticket.',
#                 'isSuccess': False
#             }, status=status.HTTP_403_FORBIDDEN) 
        
#         try:
#             unit = HouseUnit.objects.select_related('house').get(pk=pk)
#         except HouseUnit.DoesNotExist:
#             return Response({
#                 'msg': 'Unit not found', 
#                 'isSuccess': False
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         ticket_exists = Ticket.objects.filter(subject=request.data['subject'], unit= pk).exists()
#         if ticket_exists:
#             return Response({
#                 'msg': 'Ticket with specified details already exists',
#                 'isSuccess': False
#             }, status=status.HTTP_400_BAD_REQUEST)   
        
#         # deserialize user input -> convert incoming json to model instance
#         serializer = TicketSerializer(data=request.data, context={'unit': unit})
#         # validate the data
#         if serializer.is_valid():
#             # save the data into the database
#             ticket = serializer.save()
#             send_ticket_notification_to_landlord(request.user.pk, pk)
#             return Response({
#                 "msg": "Ticket added successfully",
#                 "id": ticket.pk,
#                 "data": serializer.data,
#                 'isSuccess': True
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # View all tickets
# class TicketsListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):

#         # if request.user.user_type != 'Landlord':
#         #     return Response({
#         #         'msg': 'User does not have the correct role to register a house.',
#         #         'isSuccess': False
#         #     }, status=403)  # Forbidden
        
#         tickets = Ticket.objects.filter(unit__house__owner=request.user)  
#         data = [] 
#         for ticket in tickets:
#             serializer = TicketSerializer(ticket)  # serializes the model instance to dict
#             ticket_data = {
#                 "id": ticket.pk,
#                 "data": serializer.data,
#             }
#             data.append(ticket_data)
#         return Response({
#             "response_data": data
#         }, status=status.HTTP_200_OK)
    
# # View a specific ticket's info
# class TicketDetailsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, ticket_id):
#         try:
#             ticket = Ticket.objects.get(id=ticket_id)
#         except Ticket.DoesNotExist:
#             return Response({
#                 'msg': 'Ticket not found',
#                 'isSuccess': False
#             }, status=status.HTTP_404_NOT_FOUND)
#         serializer = TicketSerializer(ticket, many=False)
#         return Response({
#             "id": ticket.id,
#             "data": serializer.data,
#             "isSuccess": True
#         }, status=status.HTTP_200_OK)

# # Edit a specific ticket
# class TicketUpdateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, ticket_id):
#         try:
#             ticket = Ticket.objects.get(id=ticket_id)
#         except Ticket.DoesNotExist:
#             return Response({
#                 'msg': 'Ticket not found',
#                 'isSuccess': False
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         if request.user.user_type == 'Landlord':
#             allowed_fields = ['category', 'status']
#             # data = {key: value for key, value in request.data.items() if key in allowed_fields}
#         elif request.user.user_type == 'Tenant':
#             allowed_fields = ['subject']
#             # data = {key: value for key, value in request.data.items() if key in allowed_fields}

#         data = {key: value for key, value in request.data.items() if key in allowed_fields}

#         serializer = TicketSerializer(instance=ticket, data=data, partial=True)
#         if serializer.is_valid():
#             old_status = ticket.status
#             updated_ticket = serializer.save()
            
#             if old_status != 'Open' and updated_ticket.status == 'Open' and request.user.user_type == 'Landlord':

#                 send_ticket_notification_to_tenant(ticket.unit.pk, request.user.pk)
#             return Response({
#                 "msg": "Update Successful",
#                 "data": serializer.data,
#                 "isSuccess": True
#             }, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# # delete a specific ticket
# class DeleteTicketView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
    
#     def delete(self, request, ticket_id):
#         if request.user.user_type != 'Landlord':
#             return Response({
#                 'msg': 'User does not have the correct role to delete a ticket.',
#                 'isSuccess': False
#             }, status=status.HTTP_403_FORBIDDEN)
        
#         try:
#             ticket = Ticket.objects.get(ticket_id=ticket_id)
#             ticket.delete()
#             return Response({
#                 "msg": "Ticket Deleted Successfully",
#                 "isSuccess": True
#             }, status=200)
#         except Ticket.DoesNotExist:
#             return Response({
#                 'msg': 'Ticket not found',
#                 'isSuccess': False
#             }, status=status.HTTP_400_BAD_REQUEST)