from django.urls import path
from .views import *

urlpatterns = [
    path("create", PaymentAddView.as_view()),
]
