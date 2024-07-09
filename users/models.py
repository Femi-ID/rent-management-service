from django.db import models
from django.contrib.auth.models import User, AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from .enums import UserType
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, user_type, **extra_fields):
        # **extra_fields are the fields that come with the default django user model
        if not email:
            raise ValueError("Email must be provided!!")
        if not password:
            raise ValueError("Password must be provided!!")
        
        # to create the user object
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, first_name, last_name, user_type, date_of_birth, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is_staff must be 'True'")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser must be 'True'")

        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser is_active must be 'True'")

        return self.create_user(email=email, password=password, 
                                date_of_birth=date_of_birth,
                                first_name=first_name,
                                last_name=last_name,
                                user_type=user_type, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    # std_user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4,  primary_key=True, editable=False, unique=True)
    username = models.CharField(max_length=250, null=False, unique=True)
    email = models.EmailField(max_length=250, null=False, unique=True)
    phone_number = models.CharField(max_length=14, null=False)
    date_of_birth = models.DateField()
    user_type = models.CharField(max_length=8, choices=UserType.choices, default=UserType.TENANT)
    created_at = models.DateTimeField(auto_now_add=True)

    # create UserManager object to use this custom model.
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'user_type', 'phone_number', 'date_of_birth']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Username: {self.username} >> UserType: {self.user_type} >> email: {self.email}"

    # def addTenantInfo(self):
        # if self.user_type == 'TENANT':
        #     job_description = models.TextField(blank=True, null=True)



# class LeaseAgreement(models.Model):
#     house = models.ForeignKey(User, related_name='lease_agreement', on_delete=models.DO_NOTHING, limit_choices_to={'user_type': 'LANDLORD'})
#     document = models.FileField()


# User.add_to_class





