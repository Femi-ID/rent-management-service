from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username', 'is_active', 'email', 'phone_number', 'user_type', 'created_at')
    list_filter = ('first_name', 'last_name', 'username', 'user_type', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'user_type', )
