from django.shortcuts import redirect, get_object_or_404, render,HttpResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Cart, CartItem, Order
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from .utils import *
from django.urls import reverse
from .utils import (
    get_cart_and_type, apply_coupon_to_cart, clear_cart,
    validate_checkout_profile, validate_stock,
    create_order_and_items, render_checkout_context, handle_payment,
    send_order_confirmation_email
)
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, cart_type = get_cart_and_type(request)
        return render(request, 'cart_detail.html', {
            'cart': cart,
            'cart_type': cart_type,
            'original_price': cart.calculate_original_price(),
            'discounted_price': cart.calculate_discounted_price()
        })

class AddCartItemView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart, cart_type = get_cart_and_type(request)
        success, message = check_stock_before_add(cart, product, quantity)
        if not success:
            messages.error(request, message)
        return redirect(f'/cart/?type={cart_type}')

class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = cart_item.cart
        new_quantity = int(request.POST.get('quantity'))
        product = cart_item.product
        if not is_product_in_stock(product, new_quantity):
            messages.error(request, f"Only {product.stock} items of {product.name} are in stock.")
        elif new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()
            if cart.is_buy_now and not cart.items.exists():
                cart.delete()
        return redirect(f'/cart/?type={"buy_now" if cart.is_buy_now else "regular"}')

class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        if cart.is_buy_now and not cart.items.exists():
            cart.delete()
        return redirect(f'/cart/?type={"buy_now" if cart.is_buy_now else "regular"}')

class BuyNowView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart.get_cart(request.user, 'buy_now')
        if not is_product_in_stock(product, quantity):
            messages.error(request, f"Only {product.stock} items of {product.name} are in stock.")
            return redirect(reverse('cart_detail') + '?type=buy_now')
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=product.price)
        return redirect(reverse('cart_detail') + '?type=buy_now')

class ApplyCouponView(LoginRequiredMixin, View):
    def post(self, request):
        cart_type = request.POST.get('cart_type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        if apply_coupon_to_cart(cart, request.POST.get('coupon_code'), request.user):
            messages.success(request, "Coupon applied successfully.")
        else:
            messages.error(request, "Invalid or expired coupon.")
        return redirect(f"{reverse('checkout')}?type={cart_type}")

class RemoveCouponView(LoginRequiredMixin, View):
    def post(self, request):
        cart_type = request.POST.get('cart_type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        cart.coupon = None
        cart.save()
        messages.info(request, "Coupon removed.")
        return redirect(f"{reverse('checkout')}?type={cart_type}")

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart, cart_type = get_cart_and_type(request)
        if not cart.items.exists():
            return redirect('cart_detail')
        context = render_checkout_context(request, cart, cart_type)
        return render(request, 'checkout.html', context)

@login_required
def process_order_payment(request):
    if request.method != 'POST':
        return HttpResponse("Invalid Request", status=400)

    user = request.user
    cart_type = request.POST.get('cart_type', 'regular')
    payment_method = request.POST.get('payment_method')
    cart = Cart.get_cart(user, cart_type)

    if not cart.items.exists():
        return HttpResponse("Your cart is empty.", status=400)

    is_valid, error_msg = validate_checkout_profile(user)
    if not is_valid:
        messages.error(request, error_msg)
        return redirect('profile')

    is_stock_valid, error_msg = validate_stock(cart)
    if not is_stock_valid:
        messages.error(request, error_msg)
        return redirect('checkout')

    try:
        with transaction.atomic():
            order = create_order_and_items(user, cart)
            if payment_method == 'cod' or payment_method == 'upi':
                handle_payment(order, payment_method)
                send_order_confirmation_email(user, order)
                messages.success(request, "Order placed successfully!")
                return redirect('home')
            elif payment_method == 'card':
                return redirect('stripe_checkout', order_id=order.id)
            else:
                messages.error(request, "Unsupported payment method.")
                return redirect('checkout')
    except Exception as e:
        print(f"Payment processing failed: {e}")
        messages.error(request, "Something went wrong while processing your payment.")
        return redirect('checkout')

@login_required
def stripe_checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',
                        'unit_amount': int(order.final_price * 100),
                        'product_data': {'name': f"Order #{order.id}"},
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            customer_email=request.user.email,
            metadata={'order_id': order.id},
            success_url=request.build_absolute_uri(reverse('home')) + '?success=true',
            cancel_url=request.build_absolute_uri(reverse('checkout')),
        )
        return redirect(checkout_session.url)
    except Exception as e:
        print(f"Stripe session error: {e}")
        messages.error(request, "Unable to start Stripe checkout.")
        return redirect('checkout')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata'].get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'COMPLETED'
            order.save()
            send_order_confirmation_email(order.user, order)
        except Order.DoesNotExist:
            print(f"Order not found: {order_id}")

    return HttpResponse(status=200)
