from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from products.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('allauth.urls')),
    # path('search/', SearchView.as_view(), name='search'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)