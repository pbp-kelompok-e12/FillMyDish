from curses.ascii import isalpha

from django.contrib import messages
from django.core import serializers
from django.http import Http404, HttpResponse
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
from django_ratelimit.decorators import ratelimit
from recipefinder.models import RecipeCache, Recipe
from moderation.models import SuspiciousRequest
from saved_recipe.models import SavedRecipe
from .wordlist import EQUIPMENT
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
API_URL = "https://api.spoonacular.com/recipes/complexSearch"
# Create your views here.
def find_recipe(request):
    return render(request, "find.html")

@login_required(login_url="/login")
def input_ingredients(request):
    return render(request, "input.html")

def normalize(item):
    return {
        "id": item.get("id"),
        "title": item.get("title", "Untitled"),
        "image": item.get("image", ""),
        "summary": item.get("summary", ""),
        "instructions": item.get("analyzedInstructions"),
        "nutrition": item.get("nutrition"),
        "source": item.get("sourceUrl", "")
    }

def split_csv(raw):
    return [i.strip() for i in raw.split(",") if i.strip()]

def get_recipe_cache():
    today = datetime.now(WIB).date()
    recipe_cache, _ = RecipeCache.objects.get_or_create(id=1)
    if recipe_cache.last_reset != today:
        updated = RecipeCache.objects.filter(id=1).exclude(last_reset=today).update(recipes={}, last_reset=today)
        if updated:
            recipe_cache.refresh_from_db()
    return recipe_cache

def suspicious(ingredients):
    vowels = ["a", "e", "i", "o", "u", "y"]
    for ingredient in ingredients:
        text = ingredient.lower()
        vowel_count = 0
        consonant_count = 0
        for letter in text:
            if letter in vowels:
                vowel_count += 1
            elif letter.isalpha():
                consonant_count += 1
        if(vowel_count == 0 
                   or consonant_count == 0
                   or len(text) > 30 
                   or len(text) == 1
                   or len(text) > 9*vowel_count):
            return True
    return False
        
@login_required(login_url="login")
@ratelimit(key="ip", rate="5/m", block=False)
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
    if request.limited:
        if error is None:
            error = "Too many searches, Please try again later.\n"
        elif error is not None:
            error += "Too many searches, Please try again later.\n"
    if suspicious(ingredients):
        sus = SuspiciousRequest.objects.create(user=request.user, arguments=list(ingredients))
        if request.limited:
            sus.arguments.append("Hit rate limit")
            sus.save()
    elif ingredients and error is None:
        key = "recipes:" + "|".join([
            ",".join(sorted(i.lower() for i in ingredients)),
            ",".join(sorted(e.lower() for e in exclude)),
            ",".join(sorted(t.lower() for t in tools)),
        ])
        recipe_cache = get_recipe_cache()
        recipes = recipe_cache.recipes.get(key)
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
                recipe_models = []
                for r in recipes:
                    Recipe.objects.update_or_create(id=r["id"], defaults={"title":r["title"], "image":r.get("image"), "summary":r.get("summary"), "instructions":r.get("instructions"), "nutrients":r.get("nutrition"), "source":r.get("source")})
                    recipe_models.append(get_object_or_404(Recipe, pk=r["id"]))
                recipe_cache.recipes[key] = recipes
                recipe_cache.save()
                recipes = recipe_models
            except (requests.RequestException, ValueError):
                recipes, error = [], "We couldn't load recipes right now. Please try again."
        else:
            recipes = [get_object_or_404(Recipe, pk=recipe["id"]) for recipe in recipes]
    context = {
        "ingredients": ingredients,
        "recipes": recipes,
        "error": error,
    }
    return render(request, "results.html", context)

def show_recipe_details(request, recipe_id):
    try:
        recipe = get_object_or_404(Recipe, pk=recipe_id)
    except Http404:
        return render(request, "details.html", {"error": f"Could not find recipe with id {recipe_id}"})
    nutrition = recipe.nutrients.get("nutrients")
    instructions = recipe.instructions[0].get("steps")
    steps = [step for step in instructions]
    already_saved = (
        request.user.is_authenticated
        and SavedRecipe.objects.filter(
            user=request.user,
            source_recipe=recipe
        ).exists()
    )
    context = {
        "nutrients": nutrition,
        "steps": steps,
        "title": recipe.title,
        "summary": recipe.summary,
        "image": recipe.image,
        "source": recipe.source,
        "recipe_id": recipe.id,
        "already_saved": already_saved,
    }
    return render(request, "details.html", context)