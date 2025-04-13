from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import CartItem,Cart

@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user', 'coupon', 'calculate_original_price', 'calculate_discounted_price']
    search_fields = ["user__username", "coupon__code"]

@register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['cart', 'product__name', 'quantity', 'price']
    search_fields = ["cart__user__username", "product__name"]