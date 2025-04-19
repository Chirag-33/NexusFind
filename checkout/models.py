from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils.timezone import now
from customer.models import CustomerAddress

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL, related_name="carts")
    is_buy_now = models.BooleanField(default=False)

    def calculate_original_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def calculate_discounted_price(self):
        total = self.calculate_original_price()
        if self.coupon and self.coupon.is_active and self.coupon.valid_from <= now() and self.coupon.valid_until >= now():
            if self.coupon.discount_type == "PERCENT":
                total -= total * (self.coupon.discount_value / 100)
            elif self.coupon.discount_type == "FLAT":
                total -= self.coupon.discount_value
        return max(total, 0)

    @classmethod
    def get_cart(cls, user, cart_type='regular'):
        is_buy_now = cart_type == 'buy_now'
        return cls.objects.get_or_create(user=user, is_buy_now=is_buy_now)[0]

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

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=10, choices=(("PERCENT", "PERCENT"), ("FLAT", "FLAT")))
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_usage = models.PositiveIntegerField(null=True, blank=True)
    max_usage_per_user = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coupon Usage"
        verbose_name_plural = "Coupon Usages"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=(("PENDING", "PENDING"), ("SHIPPED", "SHIPPED"), ("PROCESSING", "PROCESSING"), ("DELIVERED", "DELIVERED"), ("CANCELLED", "CANCELLED"), ("COMPLETED", "COMPLETED"), ("PAYMENT_FAILED", "PAYMENT_FAILED")))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    delivery_address = models.ForeignKey(CustomerAddress, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.user.id) + " - " + str(self.total_price)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order ID: {self.order.id})"