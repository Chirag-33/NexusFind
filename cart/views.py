from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.contrib import messages
from cart.models import Cart, CartItem
from products.models import Product
from orders.models import Order, Coupon, CouponUsage
from django.contrib.auth.decorators import login_required


class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_type = request.GET.get('type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        return render(request, 'cart_detail.html', {
            'cart': cart,
            'cart_type': cart_type,
            'original_price': cart.calculate_original_price(),
            'discounted_price': cart.calculate_discounted_price(),
        })

class AddCartItemView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart_type = request.GET.get('type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        existing_item = cart.items.filter(product=product).first()
        if cart_type == 'buy_now':
            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
            else:
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
        cart_type = "buy_now" if cart.is_buy_now else "regular"
        cart_item.delete()
        if cart.is_buy_now and not cart.items.exists():
            cart.delete()
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
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
        if coupon:
            now_time = now()
            if coupon.valid_from <= now_time <= coupon.valid_until:
                user_usage = CouponUsage.objects.filter(user=request.user, coupon=coupon).count()
                if not coupon.max_usage_per_user or user_usage < coupon.max_usage_per_user:
                    cart.coupon = coupon
                    cart.save()
                    CouponUsage.objects.create(user=request.user, coupon=coupon)
        return redirect('cart_detail')

class RemoveCouponView(LoginRequiredMixin, View):
    def post(self, request):
        cart = Cart.get_cart(request.user)
        cart.coupon = None
        cart.save()
        return redirect('cart_detail')

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart_type = request.GET.get('type', 'regular')
        cart = Cart.get_cart(request.user, cart_type)
        if not cart.items.exists():
            return redirect('cart_detail')
        return render(request, 'checkout.html', {
            'cart': cart,
            'original_price': cart.calculate_original_price(),
            'discounted_price': cart.calculate_discounted_price(),
            'cart_type': cart_type,
        })

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

        order = Order.objects.create(
            user=request.user,
            status="PENDING",
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
