from django.urls import  path
from .views import HomeView, AboutView, ContactView, SearchView, profile_view, ProductDetailView, info_page_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home/', homeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('search/' ,SearchView.as_view(), name='search'),
    path('profile/', profile_view, name='profile'),
    path('product_detail/<int:product_id>/', ProductDetailView.as_view() , name='product_detail'),
    path('<str:page_type>', info_page_view, name='info_page')
]   