from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User

custom_user = get_user_model()


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = [
            'id', 'is_active',
            'first_name', 'middle_name', 'last_name', 'username', 
            'email', 'phone_number', 'user_type', 'house_address', 'user_image'
        ]


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = [
            'first_name', 'middle_name', 'last_name', 'username', 
            'email', 'password', 'phone_number', 
            'date_of_birth', 'user_type', 'house_address', 'user_image'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'house_address', 'phone_number', 'job_title', 'user_image']