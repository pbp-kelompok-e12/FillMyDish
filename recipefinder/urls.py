from django.urls import path

from recipefinder.views import *

app_name = "recipefinder"

urlpatterns = [
    path("find/", find_recipe, name="find_recipe"),
    path("find/input/", input_ingredients, name="input_ingredients"),
    path("recipes/", show_recipes, name="show_recipes"),
]