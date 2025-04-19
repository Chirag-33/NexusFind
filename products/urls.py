from django.urls import path
from .views import HomeView, AboutView, ContactView, SearchView, ProductDetailView, SignUpView, SignInView, SignOutView, info_page_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('search/', SearchView.as_view(), name='search'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
    path('product_detail/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('info_page/<str:page_type>/', info_page_view, name='info_page'),
]