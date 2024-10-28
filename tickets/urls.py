from . import views
from django.urls import path

urlpatterns = [
    path("create-ticket/<int:pk>/", views.CreateTickets.as_view(), name="create_ticket"),
    path("tickets/", views.TicketsListView.as_view(), name="ticket_list"),
    path("ticket/<int:ticket_id>/", views.TicketDetailsView.as_view(), name="ticket_detail"),
    path("update-ticket/<int:ticket_id>/", views.TicketUpdateView.as_view(), name="update_ticket"),
    path("delete-ticket/<int:ticket_id>/", views.DeleteTicketView.as_view(), name="delete_ticket"),
]