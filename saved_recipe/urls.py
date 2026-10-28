from django.urls import path
from . import views

urlpatterns = [
    path("", views.saved_recipe_page, name="saved_recipe"),
]