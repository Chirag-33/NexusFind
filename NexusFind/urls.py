from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include(('product.urls', 'product'), namespace='product')),
    path('cart/', include(('checkout.urls', 'checkout'), namespace='checkout')),
    path('customer/', include(('customer.urls', 'customer'), namespace='customer')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)