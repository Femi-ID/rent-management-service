from django.urls import path
from . import views

urlpatterns = [
    path('create-house/', views.CreateHouse.as_view(), name='create-house'),
    path('list-houses/<str:owner_id>/', views.ListHousesAndUnits.as_view(), name='list-house'),

    path('onboard-user/<int:house_unit_id>', views.OnboardUser.as_view(), name='onboard-user'),   
]
