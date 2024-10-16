from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView

from users.serializers import UserSerializer
from .models import User
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from django.http import JsonResponse
from core.models import HouseUnit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="This view displays the user's personal information. POST /payments/initialize-payment/{house_unit_id}",
        manual_parameters=[
            openapi.Parameter(
                'house_unit_id',
                openapi.IN_PATH,
                description="The ID of the house unit",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user making payment.'),
            },
        ),
        responses={
            201: openapi.Response(description="Payment initialized"),
            400: openapi.Response(description="Bad request"),
        }
    )
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        if user:
            serializer = UserSerializer(user)
            return Response({'User info': serializer.data})
        else:
            return Response({'error': 'User account does not exist.'})


