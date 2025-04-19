import random
import string
from django.utils.timezone import now
from .models import Cart, Coupon, CouponUsage

def generate_tracking_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_cart_and_type(request):
    cart_type = request.GET.get('type', 'regular')
    cart = Cart.get_cart(request.user, cart_type)
    return cart, cart_type

def apply_coupon_to_cart(cart, coupon_code, user):
    coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
    now_time = now()
    if not coupon:
        return False
    if not (coupon.valid_from <= now_time <= coupon.valid_until):
        return False
    usage_count = CouponUsage.objects.filter(user=user, coupon=coupon).count()
    if coupon.max_usage_per_user and usage_count >= coupon.max_usage_per_user:
        return False
    cart.coupon = coupon
    cart.save()
    CouponUsage.objects.create(user=user, coupon=coupon)
    return True

def clear_buy_now_cart(cart):
    cart.items.all().delete()
    cart.delete()