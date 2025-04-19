from django.contrib import admin
from .models import Profile, CustomerAddress
from unfold.admin import ModelAdmin

@admin.register(CustomerAddress)
class CustomerAddressAdmin(ModelAdmin):
    list_display = ['user', 'state', 'country', 'pincode']
    search_fields = ["user__email", "address_line_1", "address_line_2", "city", "state", "country", "pincode"]
    list_filter = ['address_type']

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ['user', 'phone_number', 'email']
    search_fields = ['user__username', 'user__email']