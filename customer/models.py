from django.db import models
from django.contrib.auth.models import User
from django import forms

class CustomerAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=100, null=True)
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    address_type = models.CharField(max_length=10, choices=(("H", "Home"), ("B", "Work"), ("O", "Other")))
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)

    class Meta:
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"

    def __str__(self):
        return f"{self.get_address_type_display()} - {self.address_line_1 or self.city}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pic', blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, blank=True)
    address = models.ForeignKey(CustomerAddress, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_email(self, new_email):
        if self.email != new_email:
            self.email = new_email
            self.save()
    
    def get_full_address(self):
        return f"{self.address.address_line_1}, {self.address.city}, {self.address.state}, {self.address.country} - {self.address.pincode}" if self.address else "No Address"

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email','profile_picture','phone_number']

class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerAddress
        fields = ['address_line_1','address_line_2','address_type','city','state','country','pincode']