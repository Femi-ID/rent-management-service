from django.urls import path
from . import views

urlpatterns = [
    path('create-house/', views.CreateHouse.as_view(), name='create-house'), 
    path('list-houses/<str:owner_id>/', views.ListHousesAndUnits.as_view(), name='list-house'),
    path('register/<str:house_id>/', views.CreateHouseUnit.as_view(), name= 'create-unit'),

    path('<str:pk>/', views.CreateHouse.as_view(), name='house-detail'),
    path('update/<str:pk>/', views.CreateHouse.as_view(), name='house-update'),
    path('delete/<str:pk>/', views.CreateHouse.as_view(), name='house-delete'),

    path('unit/<str:pk>/', views.CreateHouseUnit.as_view(), name='unit-detail'),
    path('unit/update/<str:pk>/', views.CreateHouseUnit.as_view(), name='unit-update'),
    path('unit/delete/<str:pk>/', views.CreateHouseUnit.as_view(), name='unit-delete'),
    path('units/<str:house_id>/', views.ListUnitsUnderHouse.as_view(), name='list-units'),

    path('create-lease/<str:pk>/', views.LeaseAgreementView.as_view(), name='create-lease'),
    path('lease/delete/<str:pk>/', views.LeaseAgreementView.as_view(), name='lease-delete'),
    path('lease/all/<str:house_id>/', views.ListAgreementsUnderHouse.as_view(), name='list-leases'),
    path('lease/<str:pk>/', views.LeaseAgreementView.as_view(), name='lease-detail'), 

]  