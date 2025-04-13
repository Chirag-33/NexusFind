from django.db import models
from django.contrib.auth.models import User

class CustomerAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    phone = models.IntegerField()
    email = models.EmailField(unique=True)
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
        return self.address_line_1 or "Unnamed Address"