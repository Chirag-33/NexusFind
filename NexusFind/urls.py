from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('products.urls')),
    path('cart/', include('checkout.urls')),
    path('customer/', include('customer.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)