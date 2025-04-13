from django.db import models
from django.contrib.auth.models import User
from orders.models import Coupon, CouponUsage
from products.models import Product
from django.utils.timezone import now

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL, related_name="carts")
    is_buy_now = models.BooleanField(default=False)

    def calculate_original_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def calculate_discounted_price(self):
        total = self.calculate_original_price()
        if self.coupon and self.coupon.is_active and self.coupon.valid_from <= now() and self.coupon.valid_until >= now():
            if self.coupon.discount_type == "PERCENT": total -= total * (self.coupon.discount_value / 100)
            elif self.coupon.discount_type == "FLAT": total -= self.coupon.discount_value
        return max(total, 0)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"{'Buy Now' if self.is_buy_now else 'Regular'} Cart for {self.user} with {self.items.count()} items"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Cart ID: {self.cart.id})"