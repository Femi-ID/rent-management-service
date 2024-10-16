from . import views
from django.urls import path

urlpatterns = [
    path('info/', views.UserProfile.as_view(), name='user-profile'),
]
