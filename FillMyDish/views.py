import secrets

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Profile
from .forms import RegisterForm, LoginForm, ProfileForm, ConnectionFormSet

# views.py -> menangani tampilan profil dan proses edit profil pengguna, serta proses login, logout, 
#             dan pendaftaran akun baru. Juga menangani integrasi login dengan Google OAuth.

def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to FillMyDish.")
            return redirect("profile")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("profile")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def google_login_view(request):
    """Start the Google OAuth authorization-code flow."""
    if request.user.is_authenticated:
        return redirect("profile")

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(request, "Google login is not configured yet. Please use your email and password.")
        return redirect("login")

    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    redirect_uri = request.build_absolute_uri(reverse("google_callback"))
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    from urllib.parse import urlencode
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


def google_callback_view(request):
    expected_state = request.session.pop("google_oauth_state", None)
    if not expected_state or request.GET.get("state") != expected_state:
        messages.error(request, "Google sign-in could not be verified. Please try again.")
        return redirect("login")

    if request.GET.get("error"):
        messages.error(request, "Google sign-in was cancelled or denied.")
        return redirect("login")

    code = request.GET.get("code")
    if not code or not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(request, "Google sign-in is not configured correctly.")
        return redirect("login")

    redirect_uri = request.build_absolute_uri(reverse("google_callback"))
    try:
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
        user_response = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        user_response.raise_for_status()
        google_user = user_response.json()
    except (requests.RequestException, KeyError, ValueError):
        messages.error(request, "Could not complete Google sign-in. Please try again.")
        return redirect("login")

    email = google_user.get("email", "").strip().lower()
    if not email or not google_user.get("email_verified"):
        messages.error(request, "Google must provide a verified email address to sign in.")
        return redirect("login")

    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        base_username = email.split("@", 1)[0][:140] or "google_user"
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username[:140-len(str(suffix))]}{suffix}"
            suffix += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=google_user.get("given_name", "")[:150],
            last_name=google_user.get("family_name", "")[:150],
        )

    login(request, user)
    messages.success(request, f"Welcome, {user.get_short_name() or user.username}!")
    return redirect("profile")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required(login_url="login")
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {
        "profile": profile,
        "profile_user": request.user,
        "is_own_profile": True,
    })


def user_profile_view(request, username):
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    return render(request, "profile.html", {
        "profile": profile,
        "profile_user": profile_user,
        "is_own_profile": request.user.is_authenticated and request.user.pk == profile_user.pk,
    })


@login_required(login_url="login")
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        formset = ConnectionFormSet(request.POST, instance=profile)
        if form.is_valid() and formset.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            # Sinkronisasi dengan model User bawaan Django
            request.user.username = profile.username
            request.user.email = profile.email
            request.user.save()
            profile.save()
            formset.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
        formset = ConnectionFormSet(instance=profile)

    return render(request, "edit_profile.html", {
        "form": form,
        "formset": formset,
        "profile": profile,
    })
