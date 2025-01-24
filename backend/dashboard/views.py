from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

from payments.models import Payment


@login_required
@user_passes_test(
    lambda u: u.is_staff, login_url="login"
)  # Redirect to login if not staff
def dashboard(request):
    payments = Payment.objects.filter(sponsor__payment_success=True).select_related(
        "sponsor"
    )
    return render(request, "dashboard/dashboard.html", {"payments": payments})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                auth_login(request, user)
                return redirect("dashboard")
            else:
                messages.error(
                    request, "You are not authorized to access the admin dashboard."
                )
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "dashboard/login.html")


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("login")  # Redirect to the custom login page
