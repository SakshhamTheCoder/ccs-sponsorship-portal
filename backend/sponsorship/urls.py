from django.urls import path
from .views import *

urlpatterns = [
    path("add", SponsorshipAddView.as_view()),
]
