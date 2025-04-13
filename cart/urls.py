# urls.py
from django.urls import path
from .views import CartDetailView, AddCartItemView, UpdateCartItemView, RemoveCartItemView, ApplyCouponView, RemoveCouponView

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart_detail'),
    path('items/add/<int:product_id>/', AddCartItemView.as_view(), name='add_cart_item'),
    path('items/<int:item_id>/update/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('items/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('apply_coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('remove_coupon/', RemoveCouponView.as_view(), name='remove_coupon'),
]