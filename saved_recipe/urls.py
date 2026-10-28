from django.urls import path
from . import views

urlpatterns = [
    path("", views.saved_recipe_page, name="saved_recipe"),
    path("create/", views.create_saved_recipe, name="create_saved_recipe"),
    path("<int:pk>/update/", views.update_saved_recipe, name="update_saved_recipe"),
    path("<int:pk>/delete/", views.delete_saved_recipe, name="delete_saved_recipe"),
]