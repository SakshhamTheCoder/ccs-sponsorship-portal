from django.urls import path
from .views import *

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("login/", login_view, name="login"),
]
