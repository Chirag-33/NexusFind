from django.db import models
from django import forms
from django.contrib.auth.models import User
from customer.models import CustomerAddress
class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField("product_category_image", blank=True, null=True)
    product_type = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField('product_image')
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveBigIntegerField(default=0)

    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

class ProductHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    file_path = models.FileField(upload_to='attachments/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Message from ' + self.name + ' - ' + self.email + ' on ' + self.created_at.strftime('%Y-%m-%d')

class Profile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pic', blank=True, null=True)
    email = models.EmailField(unique = True )
    phone_number = models.CharField(max_length=10 , blank=True)
    address = models.ForeignKey(CustomerAddress, on_delete=models.CASCADE, null=True, blank=True)

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"










class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone_number','email']