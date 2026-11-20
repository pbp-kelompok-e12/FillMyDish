from django.urls import path

from recipefinder.views import *
from recipefinder.api_views import *

app_name = "recipefinder"

urlpatterns = [
    path("find/", find_recipe, name="find_recipe"),
    path("find/input/", input_ingredients, name="input_ingredients"),
    path("recipes/", show_recipes, name="show_recipes"),
    path("recipes/<int:recipe_id>/", show_recipe_details, name="show_recipe_details"),
    path("api/recipes/", RecipeSearchAPIView.as_view(), name="api_show_recipes"),
    path("api/recipes/<int:recipe_id>/", RecipeDetailAPIView.as_view(), name="api_show_recipe_details"),
]