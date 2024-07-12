"""
Django settings for Rent_Management project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import dj_database_url
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')
# DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(" ")
# ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # applications
    'users',
    # paystack implementation
    'accounts', 
    'payments',
    'wallets',
    'core', 

    # added dependencies
    'rest_framework',
    'djoser',
    'corsheaders',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    # corsheaders middleware
    "corsheaders.middleware.CorsMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'Rent_Management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Rent_Management.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
database_url = os.environ.get('DATABASE_URL')
DATABASES['default'] = dj_database_url.parse('postgresql://rentdb_owner:JTG6o8VCbXxH@ep-falling-river-a2gz5hjy.eu-central-1.aws.neon.tech/rentdb?sslmode=require')

# DATABASES = {
#   'default': {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': config('PGDATABASE'),
#     'USER': config('PGUSER'),
#     'PASSWORD': config('PGPASSWORD'),
#     'HOST': config('PGHOST'),
#     'PORT': config('PGPORT', 5432),
#     'OPTIONS': {
#       'sslmode': 'require',
#     },
#   }
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_ALL_ORIGINS = True  # CHANGE THIS DURING PRODUCTION


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated'
    ),
}

# simple jwt configuration for  authorization header
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT', 'Bearer'),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=2)
}

DJOSER = {
    # sign up user
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'USER_CREATE_PASSWORD_RETYPE': True, # pass re-password to /users endpoint.
    'ACTIVATION_URL': 'auth/activate/?uid={uid}&token={token}', # url sent to the email to activate new user

    # reset user password
    'PASSWORD_RESET_CONFIRM_URL': 'password-reset/{uid}/{token}', # wil be appended to DOMAIN and sent to user email
    # 'SET_PASSWORD_RETYPE': True, # pass re_new_password to /users/set_password/ (when user creates new password)
    'PASSWORD_RESET_CONFIRM_RETYPE': True, # pass re_new_password to /users/reset_password_confirm/

    'SERIALIZERS': {
        # create  new user
        'user_create': 'users.serializers.UserCreateSerializer',

        # serializer view for general users and specific users
        'user': 'users.serializers.UserSerializer', # /users endpoint
        'current_user': 'users.serializers.UserSerializer', # /users/me endpoint
    },

}

SITE_NAME = 'RENT PADI'
DOMAIN = 'localhost:8000' # (change to frontend localhost) the ACTIVATION_URL will be appended to this domain

# Email config
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')

# EMAIL_BACKEND = config('EMAIL_BACKEND')
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_PORT = config('EMAIL_PORT')
# EMAIL_USE_TLS = config('EMAIL_USE_TLS')
# EMAIL_USE_SSL = config('EMAIL_USE_SSL')
# DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")

# PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')
# PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY")
