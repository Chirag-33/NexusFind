from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import Product, ProductCategory, Contact, Comment

@register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ['name', 'email', 'message', 'file_path', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_filter = ['name', 'created_at']

@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "category", "created_at")
    search_fields = ("name", "description")
    list_filter = ("category", "created_at")

@register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "image")
    search_fields = ("name", "description")

@register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('product', 'user', 'content')
    search_fields = ('product__name', 'user__username', 'content')
    list_filter = ('product', 'created_at')