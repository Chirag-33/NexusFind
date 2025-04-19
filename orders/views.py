import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Order, OrderItem, Coupon, CouponUsage
from customer.models import CustomerAddress
from products.models import Profile

def generate_tracking_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

from cart.models import Cart

@login_required
def checkout(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'email': user.email})

    if user.email and profile.email != user.email:
        profile.email = user.email
        profile.save()

    # Get the cart_type from query params
    cart_type = request.GET.get('type', 'regular')
    
    # Use your model's utility method
    cart = Cart.get_cart(user=user, cart_type=cart_type)
    
    original_price = cart.calculate_original_price()
    discounted_price = cart.calculate_discounted_price()
    random_tracking_id = generate_tracking_id()

    address = CustomerAddress.objects.filter(user=user).first()


    return render(request, 'checkout.html', {
        'cart': cart,
        'original_price': original_price,
        'discounted_price': discounted_price,
        'random_tracking_id': random_tracking_id,
        'profile': profile,
        'address': address
    })



