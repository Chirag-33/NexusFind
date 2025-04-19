from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from cart.models import CartItem
from products.models import Product
from orders.models import Order
from products.models import Profile
from customer.models import CustomerAddress
from .utils import get_cart_and_type, generate_tracking_id, apply_coupon_to_cart, clear_buy_now_cart

class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, cart_type = get_cart_and_type(request)
        return render(request, 'cart_detail.html', {'cart': cart, 'cart_type': cart_type, 'original_price': cart.calculate_original_price(), 'discounted_price': cart.calculate_discounted_price()})

class AddCartItemView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart, cart_type = get_cart_and_type(request)
        existing_item = cart.items.filter(product=product).first()
        if cart_type == 'buy_now':
            cart.items.all().delete()
            CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=product.price)
        else:
            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
            else:
                CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=product.price)
        return HttpResponseRedirect(f'/cart/?type={cart_type}')

class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = cart_item.cart
        new_quantity = int(request.POST.get('quantity'))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()
            if cart.is_buy_now:
                cart.delete()
        return HttpResponseRedirect(f'/cart/?type={"buy_now" if cart.is_buy_now else "regular"}')

class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        if cart.is_buy_now and not cart.items.exists():
            cart.delete()
        cart_type = "buy_now" if cart.is_buy_now else "regular"
        return HttpResponseRedirect(f'/cart/?type={cart_type}')

class BuyNowView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart.get_cart(request.user, 'buy_now')
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=product.price)
        return redirect(reverse('cart_detail') + '?type=buy_now')

class ApplyCouponView(LoginRequiredMixin, View):
    def post(self, request):
        coupon_code = request.POST.get('coupon_code')
        cart = Cart.get_cart(request.user)
        success = apply_coupon_to_cart(cart, coupon_code, request.user)
        if success:
            messages.success(request, "Coupon applied successfully.")
        else:
            messages.error(request, "Invalid or expired coupon.")
        return redirect('cart_detail')

class RemoveCouponView(LoginRequiredMixin, View):
    def post(self, request):
        cart = Cart.get_cart(request.user)
        cart.coupon = None
        cart.save()
        messages.info(request, "Coupon removed.")
        return redirect('cart_detail')

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart, cart_type = get_cart_and_type(request)
        if not cart.items.exists():
            return redirect('cart_detail')
        return render(request, 'checkout.html', {'cart': cart, 'original_price': cart.calculate_original_price(), 'discounted_price': cart.calculate_discounted_price(), 'cart_type': cart_type})

class PlaceOrderView(LoginRequiredMixin, View):
    def post(self, request):
        cart_type = request.POST.get('cart_type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        cart.items.all().delete()
        if cart.is_buy_now:
            cart.delete()
        messages.success(request, 'Your order placed successfully!')
        return redirect('home')

@login_required
def process_order_payment(request):
    if request.method == 'POST':
        cart_type = request.POST.get('cart_type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        if not cart.items.exists():
            return HttpResponse("Your cart is empty.", status=400)
        payment_method = request.POST.get('payment_method')
        if payment_method not in ['card', 'razorpay', 'upi', 'cod']:
            return HttpResponse("Invalid payment method", status=400)
        order = Order.objects.create(user=request.user, status="PENDING", delivery_address=request.user.profile.address, total_price=cart.calculate_original_price(), discount_applied=cart.calculate_original_price() - cart.calculate_discounted_price(), final_price=cart.calculate_discounted_price())
        if payment_method in ['card', 'razorpay']:
            return redirect('razorpay_checkout', order_id=order.id)
        if payment_method == 'upi':
            order.status = 'COMPLETED'
        elif payment_method == 'cod':
            order.status = 'PENDING'
        order.save()
        return redirect('order_success', order_id=order.id)
    return HttpResponse("Invalid Request", status=400)