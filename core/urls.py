from django.urls import path
from . import views

urlpatterns = [
    path('create-house/', views.CreateHouse.as_view(), name='create-house'),
    path('create-house-unit/<str:house_id>/', views.CreateHouseUnit.as_view(), name='create-house-units'),
    path('list-houses/<str:owner_id>/', views.ListHouses.as_view(), name='list-house'),
    path('list-house-units/<str:owner_id>/<str:house_id>/', views.ListHouseUnits.as_view(), name='list-house'),

    path('onboard-user/', views.OnboardUser.as_view(), name='onboard-user'),
    # path('onboard-user/<int:house_unit_id>/', views.OnboardUser.as_view(), name='onboard-user'),  
    path('tenant-dashboard/', views.TenantDashboard.as_view(), name='tenant-dashboard'), 

    path('<str:house_id>/', views.HouseDetailView.as_view(), name='house-detail'),
    path('house-unit/<str:house_unit_id>/', views.HouseUnitDetailView.as_view(), name='house-unit-detail'),
    path('lease/<str:house_unit_id>/', views.LeaseAgreementView.as_view(), name='lease-agreement'), 
]
