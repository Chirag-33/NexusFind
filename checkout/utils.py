import random
import string
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Cart, CartItem, Coupon, CouponUsage, Order, OrderItem
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction

def generate_tracking_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_cart_and_type(request):
    cart_type = request.GET.get('type', 'regular')  
    cart = Cart.get_cart(request.user, cart_type)  
    return cart, cart_type

def apply_coupon_to_cart(cart, coupon_code, user):
    coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
    now_time = now()
    if not coupon: return False
    if not (coupon.valid_from <= now_time <= coupon.valid_until): return False
    usage_count = CouponUsage.objects.filter(user=user, coupon=coupon).count()
    if coupon.max_usage_per_user and usage_count >= coupon.max_usage_per_user: return False
    cart.coupon = coupon
    cart.save()
    CouponUsage.objects.create(user=user, coupon=coupon)
    return True

def clear_cart(cart):
    cart.items.all().delete()
    cart.coupon = None
    cart.save()
    if cart.is_buy_now: cart.delete()

def validate_checkout_profile(user):
    try: profile = user.profile
    except Exception: return False, "You must complete your profile before placing an order."
    if not profile.address and (not user.email or not profile.phone_number): return False, "Please add your details before placing an order."
    return True, ""

def validate_stock(cart):
    for cart_item in cart.items.all():
        product = cart_item.product
        if product.stock < cart_item.quantity: return False, f"Not enough stock for {product.name}. Only {product.stock} available."
    return True, ""

def get_or_redirect_cart(request, cart_type):
    cart = Cart.get_cart(request.user, cart_type)
    if not cart.items.exists(): return None, redirect('cart_detail')
    return cart, None

def render_checkout_context(request, cart, cart_type):
    is_valid_profile, error_msg = validate_checkout_profile(request.user)
    return {'cart': cart, 'cart_type': cart_type, 'original_price': cart.calculate_original_price(), 'discounted_price': cart.calculate_discounted_price(), 'payment_method': request.GET.get("payment_method", "card"), 'profile': getattr(request.user, 'profile', None), 'address': getattr(request.user.profile, 'address', None) if hasattr(request.user, 'profile') else None, 'can_place_order': is_valid_profile, 'validation_error_msg': error_msg}

def create_order_from_cart(user, cart):
    profile = user.profile
    return Order.objects.create(user=user, status="PENDING", delivery_address=profile.address, total_price=cart.calculate_original_price(), discount_applied=cart.calculate_original_price() - cart.calculate_discounted_price(), final_price=cart.calculate_discounted_price())

def deduct_product_stock(cart, order):
    for cart_item in cart.items.all():
        product = cart_item.product
        quantity = cart_item.quantity
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=cart_item.price)
        product.stock -= quantity
        product.save()

def handle_payment(order, method):
    if method == 'upi': order.status = 'COMPLETED'
    elif method == 'cod': order.status = 'PENDING'
    order.save()

def get_profile_address(user):
    try: return user.profile.address
    except Exception: return None

def create_order_and_items(user, cart):
    order = create_order_from_cart(user, cart)
    deduct_product_stock(cart, order)
    clear_cart(cart)
    return order

def check_stock_before_add(cart, product, quantity):
    if not is_product_in_stock(product, quantity): return False, f"Only {product.stock} items of {product.name} are in stock."
    existing_item = cart.items.filter(product=product).first()
    if cart.is_buy_now:
        cart.items.all().delete()
        CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=product.price)
    else:
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if not is_product_in_stock(product, new_quantity): return False, f"Only {product.stock} items of {product.name} are in stock."
            existing_item.quantity = new_quantity
            existing_item.save()
        else: CartItem.objects.create(cart=cart, product=product, quantity=quantity, price=product.price)
    return True, None

def is_product_in_stock(product, desired_quantity):
    return product.stock >= desired_quantity

def send_order_confirmation_email(user, order):
    subject = f"NexusFind - Order #{order.id} Confirmation"
    recipient_email = user.email
    from_email = settings.EMAIL_HOST_USER
    tracking_id = generate_tracking_id()
    item_lines = [f"{item.quantity} x {item.product.name} @ ₹{item.price}"for item in order.items.all()]
    item_text = "\n".join(item_lines)
    addr = order.delivery_address
    address_block = f"""{addr.address_line_1}{addr.address_line_2 or ''}{addr.city}, {addr.state}, {addr.country} - {addr.pincode}"""

    message = f"""
Hi {getattr(user, 'full_name', '') or user.email},

Thank you for placing your order with NexusFind!

🧾 Order Summary (Order ID: {order.id}):
----------------------------------------
{item_text}

Subtotal: ₹{order.total_price}
Discount: ₹{order.discount_applied}
Amount Paid: ₹{order.final_price}

🚚 Shipping To:
{address_block.strip()}

Your order is currently marked as: {order.status}
You can check the status via Tracking ID: {tracking_id}

We’ll notify you when it’s shipped.  
If you have any questions, feel free to reply to this email.

Thanks for choosing NexusFind!  
— Team NexusFind
""".strip()
    email = EmailMessage(subject, message, from_email, [recipient_email])
    try: email.send(fail_silently=False)
    except Exception as e: print(f"Email sending failed: {e}")