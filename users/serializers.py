from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer

custom_user = get_user_model()


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserCreateSerializer):
        fields = [
            'id', 'is_active',
            'first_name', 'last_name', 'username', 
            'email', 'phone_number', 'user_type'
        ]


class UserCreateUserSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer):
        fields = [
            'first_name', 'last_name', 'username', 
            'email', 'password', 'phone_number', 
            'date_of_birth', 'user_type',
        ]
