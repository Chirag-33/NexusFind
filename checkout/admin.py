from django.contrib.admin import register
from unfold.admin import ModelAdmin
from .models import Cart, CartItem, Order, OrderItem, Coupon, CouponUsage

@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user', 'coupon', 'calculate_original_price', 'calculate_discounted_price', 'is_buy_now']
    search_fields = ["user__username", "coupon__code"]

@register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['cart', 'product__name', 'quantity', 'price']
    search_fields = ["cart__user__username", "product__name"]

@register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['user', 'status', 'total_price', 'discount_applied', 'final_price']
    search_fields = ["user__username", "status", "total_price", "discount_applied", "final_price", ]
    list_filter = ["status"]

@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['order', 'product__name', 'quantity', 'price']
    search_fields = ["order__user__username", "product__name"]

@register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until', 'max_usage', 'max_usage_per_user']
    search_fields = ["code", "title", "description"]
    list_filter = ["is_active", "valid_from", "valid_until", "max_usage", "max_usage_per_user"]

@register(CouponUsage)
class CouponUsageAdmin(ModelAdmin):
    list_display = ['user', 'coupon', 'used_at']
    search_fields = ["user__username", "coupon__code"]