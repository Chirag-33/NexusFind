from django.contrib.admin import register
from django.contrib import admin
from .models import User, CustomerAddress
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

@register(CustomerAddress)
class CustomerAddressAdmin(ModelAdmin):
    list_display = ['user','phone', 'state', 'country', 'pincode']
    search_fields = ["user__email", "user__full_name", "address_line_1", "address_line_2", "city", "state", "country", "pincode"]
    list_filter = ['address_type']