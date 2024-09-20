from django.contrib import admin
from .models import House, HouseUnit, LeaseAgreement

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'city', 'state', 'reg_license')
    list_filter = ('address',)
    search_fields = ('owner',)

@admin.register(HouseUnit)
class HouseUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'house', 'unit_number', 'rent_price',)
    list_filter = ('availability',)
    search_fields = ('unit_number',)

@admin.register(LeaseAgreement)
class LeaseAgreementAadmin(admin.ModelAdmin):
    list_display = ('id', 'house_unit', 'document',) 
    list_filter = ('created_by',)
    search_fields = ('house_unit',)
