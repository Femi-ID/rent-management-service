from django.urls import path
from . import views

urlpatterns = [
    path('create-house/', views.CreateHouse.as_view(), name='create-house'),
    path('list-houses/<str:owner_id>/', views.ListHousesAndUnits.as_view(), name='list-house'),
]
