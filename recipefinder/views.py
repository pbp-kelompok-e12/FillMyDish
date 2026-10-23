from django.contrib import messages
from django.core import serializers
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied   
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.conf import settings
import datetime
import requests
from django.views.decorators.http import require_POST
from .wordlist import EQUIPMENT
API_URL = "https://api.spoonacular.com/recipes/complexSearch"
# Create your views here.
# @login_required(login_url="")
def find_recipe(request):
    return render(request, "find.html")

# @login_required(login_url="")
def input_ingredients(request):
    return render(request, "input.html")

def normalize(item):
    return {
        "id": item.get("id"),
        "title": item.get("title", "Untitled"),
        "image": item.get("image", ""),
        "summary": item.get("summary", ""),
        "instructions": item.get("analyzedInstructions"),
        "nutrition": item.get("nutrition")
    }

def split_csv(raw):
    return [i.strip() for i in raw.split(",") if i.strip()]
 
# @login_required(login_url="")
def show_recipes(request):
    ingredients_raw = request.GET.get("ingredients", "")
    tools_raw = request.GET.get("tools", "")
    exclude_raw = request.GET.get("exclude", "")
    ingredients = split_csv(ingredients_raw)
    tools = split_csv(tools_raw)
    exclude = split_csv(exclude_raw)
    recipes, error = [], None
    for tool in tools:
        if tool not in EQUIPMENT and error is None:
            error = f"{tool} is not recognized as a tool by the API, please try again without it\n"
        elif tool not in EQUIPMENT and error is not None:
            error += f"{tool} is not recognized as a tool by the API, please try again without it\n"
    if ingredients and error is None:
        key = "recipes:" + "|".join([
            ",".join(sorted(i.lower() for i in ingredients)),
            ",".join(sorted(e.lower() for e in exclude)),
            ",".join(sorted(t.lower() for t in tools)),
        ])
        recipes = cache.get(key)
        if recipes is None:
            try:
                response = requests.get(API_URL, 
                     params={
                        "apiKey": settings.SPOONACULAR_API_KEY,
                        "includeIngredients": ",".join(ingredients),
                        "excludeIngredients": ",".join(exclude),
                        "equipment": ",".join(tools),
                        "number": 10,
                        "sort": "min-missing-ingredients",
                        "addRecipeInformation": "true",
                        "addRecipeInstructions": "true",
                        "addRecipeNutrition": "true",
                    },
                    timeout=8,)
                response.raise_for_status()
                recipes = [normalize(x) for x in response.json().get("results", [])]
                cache.set(key, recipes, 60 * 60)
            except (requests.RequestException, ValueError):
                recipes, error = [], "We couldn't load recipes right now. Please try again."
    context = {
        "ingredients": ingredients,
        "recipes": recipes,
        "error": error,
    }
    return render(request, "results.html", context)
    