from django.urls import path
from .views import *
from orders.views import process_payment

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart_detail'),
    path('items/add/<int:product_id>/', AddCartItemView.as_view(), name='add_cart_item'),
    path('items/<int:item_id>/update/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('items/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('buy_now/<int:product_id>/', BuyNowView.as_view(), name='buy_now'),
    path('apply_coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('remove_coupon/', RemoveCouponView.as_view(), name='remove_coupon'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('place-order/', PlaceOrderView.as_view(), name='place_order'),
    path('process-payment/', process_payment, name='process_payment'),
]