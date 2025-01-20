from django.urls import path
from .views import *

urlpatterns = [
    path("create", PaymentGatewayView.as_view()),
    path("callback", PaymentCallbackView.as_view()),
]
