
from . import views
from django.urls import path

urlpatterns = [
    path('houseList/', views.HouseListView.as_view(), name = "house-list"), 
    path('houseDetails/<str:pk>', views.HouseDetailsView.as_view(), name = "houseDetails"), 
    path('delete/<str:pk>', views.DeleteHouseView.as_view(), name = "delete"), 
    path('register/', views.RegisterHouseView.as_view(), name = "registerHouse"),
    path('update/<str:pk>', views.HouseUpdateView.as_view(), name = "houseUpdate"),

     
    path('register/unit', views.RegisterUnitView.as_view(), name="registerUnit"),
    path('register/<str:pk>/', views.RegisterUnitView.as_view(), name="registerUnitWithHouse"),
    path('unitList/', views.UnitListView.as_view(), name = "unitList"), 
    path('unit/<int:pk>', views.UnitDetailsView.as_view(), name = "unitDetails"),
    path('unit/delete/<int:pk>', views.DeleteUnitView.as_view(), name = "delete"), 
    path('unit/update/<int:pk>', views.UnitUpdateView.as_view(), name = "unitUpdate"),

    path('lease/create/<int:pk>', views.CreateLeaseView.as_view(), name = "createLease"),
    path('lease/delete/<int:pk>', views.DeleteLeaseView.as_view(), name = "deleteLease"), 
    path('lease/view/<int:pk>', views.LeaseDetailsView.as_view(), name = "delete"), 
    path('lease/all', views.LeaseAgreementView.as_view(), name = "leaseList"), 

] 