from . import views
from django.urls import path

urlpatterns = [
    path('profile/<str:user_id>/', views.UserProfile.as_view(), name='user-profile'),
    path('landlord-dashboard/', views.LandlordDashboard.as_view(), name='landlord-dashboard'),
]
