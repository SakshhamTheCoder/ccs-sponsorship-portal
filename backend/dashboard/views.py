from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect("main")
        else:
            messages.error(request, "Invalid credentials or not authorized.")

    return render(request, "dashboard/login.html")


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")
