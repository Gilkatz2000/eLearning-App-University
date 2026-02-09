from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm, StatusUpdateForm
from .models import User, StatusUpdate


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("course_list")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("course_list")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def user_home(request, username):
    profile_user = get_object_or_404(User, username=username)

    updates = StatusUpdate.objects.filter(user=profile_user).order_by("-created_at")

    # Only the profile owner AND only students can post
    can_post = request.user.is_student() and request.user.id == profile_user.id
    form = StatusUpdateForm() if can_post else None

    return render(
        request,
        "accounts/user_home.html",
        {
            "profile_user": profile_user,
            "updates": updates,
            "can_post": can_post,
            "form": form,
        },
    )


@login_required
@require_POST
def post_status_update(request):
    # Only students can post
    if not request.user.is_student():
        raise PermissionDenied

    form = StatusUpdateForm(request.POST)
    if form.is_valid():
        status = form.save(commit=False)
        status.user = request.user
        status.save()

    return redirect("user_home", username=request.user.username)
