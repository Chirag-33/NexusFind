from django.urls import path
from .views import *

urlpatterns = [
    path('process_payment/', process_payment, name='process_payment'),
]