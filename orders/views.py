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

@login_required
def checkout(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'email': user.email})
    if user.email and profile.email != user.email:
        profile.email = user.email
        profile.save()
    cart = request.user.cart
    original_price = cart.total_price
    discounted_price = original_price - cart.discount_applied
    random_tracking_id = generate_tracking_id()

    return render(request, 'checkout.html', {
        'cart': cart,
        'original_price': original_price,
        'discounted_price': discounted_price,
        'random_tracking_id': random_tracking_id,
        'profile': profile,
    })

@login_required
def process_payment(request):
    if request.method == 'POST':
        cart_type = request.POST.get('cart_type', 'regular')
        cart = get_cart(request.user, cart_type)

        order = Order.objects.create(
            user=request.user,
            status="PENDING",
            total_price=cart.total_price,
            discount_applied=cart.discount_applied,
            final_price=cart.final_price,
            delivery_address=request.user.profile.address,
        )
        
        payment_method = request.POST.get('payment_method')

        if payment_method == 'card':
            return redirect('razorpay_checkout', order_id=order.id)

        elif payment_method == 'razorpay':
            return redirect('razorpay_checkout', order_id=order.id)

        elif payment_method == 'upi':
            order.status = 'COMPLETED'
            order.save()
            return redirect('order_success', order_id=order.id)

        elif payment_method == 'cod':
            order.status = 'PENDING'
            order.save()
            return redirect('order_success', order_id=order.id)

    return HttpResponse("Invalid Request", status=400)
