from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from .models import Payment, PaymentPlan, Subscription, PaymentReceipt
from users.models import User
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from django.http import JsonResponse
from core.models import HouseUnit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




