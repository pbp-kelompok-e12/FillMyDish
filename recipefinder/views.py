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
from .services import (
    get_nutrients,
    get_recipe_cache,
    get_steps,
    is_saved,
    search_recipes,
    split_csv,
)

def find_recipe(request):
    return render(request, "find.html")


@login_required(login_url="/login")
def input_ingredients(request):
    return render(request, "input.html")

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
@ratelimit(key="ip", rate="5/m", block=False, group="recipe-search")
def show_recipes(request):
    ingredients = split_csv(request.GET.get("ingredients", ""))
    tools = split_csv(request.GET.get("tools", ""))
    exclude = split_csv(request.GET.get("exclude", ""))

    recipes, errors = search_recipes(
        request.user, ingredients, tools, exclude, limited=request.limited
    )
    error = "\n".join(message for _, message in errors) or None

    return render(
        request,
        "results.html",
        {"ingredients": ingredients, "recipes": recipes, "error": error},
    )
    
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