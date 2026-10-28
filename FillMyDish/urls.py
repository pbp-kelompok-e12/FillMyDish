"""
URL configuration for FillMyDish project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Class-based views
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from FillMyDish import views

# urls.py -> mendefinisikan URL routing untuk aplikasi FillMyDish, menghubungkan URL dengan 
#            tampilan (views)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("accounts/google/login/", views.google_login_view, name="google_login"),
    path("accounts/google/callback/", views.google_callback_view, name="google_callback"),
    path("logout/", views.logout_view, name="logout"),
    path("", include("recipefinder.urls")),
    path("", include("main.urls")),
    path("review/", include("review.urls")),
    path("saved-recipes/", include("saved_recipe.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
