from django.urls import path
from .views import process_payment, checkout

urlpatterns = [
    path('process_payment/', process_payment, name='process_payment'),
    path('checkout/', checkout, name='checkout')
]