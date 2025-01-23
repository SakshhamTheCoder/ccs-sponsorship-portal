from django.urls import path
from .views import *

urlpatterns = [
    path("login", admin_login, name="admin_login"),
    path("main", dashboard, name="main"),
    path("logout", admin_logout, name="admin_logout"),
]
