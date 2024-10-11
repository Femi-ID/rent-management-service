from django.urls import path
from . import views

urlpatterns = [
    path('initialize-payment/<int:house_unit_id>/', views.AcceptPayment.as_view(), name='initialize_payment'),
    path('verify-payment/<int:house_unit_id>/', views.VerifyPayment.as_view(), name='verify_payment'),
    path('create-plan/', views.CreatePlan.as_view(), name='create_plan'),
    path('create-subscription/<int:plan_id>/', views.CreateSubscription.as_view(), name='create_sub'),
    path('payment-history/', views.PaymentHistory.as_view(), name='payment_history'),
    path('dashboard/',views.LandlordDashBoard.as_view(), name='landlord_dashboard'), 
]