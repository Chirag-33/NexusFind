from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from .models import Cart, CartItem, Product, Coupon, CouponUsage

class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        context = {'object': cart, 'original_price': cart.calculate_original_price(), 'discounted_price': cart.calculate_discounted_price(),}
        return render(request, 'cart_detail.html', context)

class AddCartItemView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.price = product.price
        cart_item.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        new_quantity = int(request.POST.get('quantity'))

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class ApplyCouponView(LoginRequiredMixin, View):
    def post(self, request):
        coupon_code = request.POST.get('coupon_code')
        cart, _ = Cart.objects.get_or_create(user=request.user)
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()

        if coupon:
            if not (coupon.valid_from <= now() <= coupon.valid_until):
                return redirect('cart_detail')

            user_usage = CouponUsage.objects.filter(user=request.user, coupon=coupon).count()
            if coupon.max_usage_per_user and user_usage >= coupon.max_usage_per_user:
                return redirect('cart_detail')

            cart.coupon = coupon
            cart.save()
            CouponUsage.objects.create(user=request.user, coupon=coupon)

        return redirect('cart_detail')

class RemoveCouponView(LoginRequiredMixin, View):
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.coupon = None
        cart.save()
        return redirect('cart_detail')