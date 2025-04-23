from django.urls import path
from .views import (
    CartDetailView, AddCartItemView, UpdateCartItemView,
    RemoveCartItemView, BuyNowView, ApplyCouponView,
    RemoveCouponView, CheckoutView,
    process_order_payment, stripe_checkout,stripe_webhook
)

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart_detail'),
    path('items/add/<int:product_id>/', AddCartItemView.as_view(), name='add_cart_item'),
    path('items/<int:item_id>/update/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('items/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('buy_now/<int:product_id>/', BuyNowView.as_view(), name='buy_now'),
    path('apply_coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('remove_coupon/', RemoveCouponView.as_view(), name='remove_coupon'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/payment/', process_order_payment, name='process_payment'),
    path('checkout/stripe/<int:order_id>/', stripe_checkout, name='stripe_checkout'),
    path('checkout/stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    ]
