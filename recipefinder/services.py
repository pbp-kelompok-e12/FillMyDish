from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings

from moderation.models import SuspiciousRequest
from recipefinder.models import Recipe, RecipeCache
from .wordlist import EQUIPMENT

WIB = timezone(timedelta(hours=7))
API_URL = "https://api.spoonacular.com/recipes/complexSearch"

TOOL_ERROR = "{} is not recognized as a tool by the API, please try again without it"
RATE_LIMIT_ERROR = "Too many searches, Please try again later."
UPSTREAM_ERROR = "We couldn't load recipes right now. Please try again."


def normalize(item):
    return {
        "id": item.get("id"),
        "title": item.get("title", "Untitled"),
        "image": item.get("image", ""),
        "summary": item.get("summary", ""),
        "instructions": item.get("analyzedInstructions"),
        "nutrition": item.get("nutrition"),
        "source": item.get("sourceUrl", ""),
    }


def split_csv(raw):
    return [i.strip() for i in raw.split(",") if i.strip()]


def get_recipe_cache():
    today = datetime.now(WIB).date()
    recipe_cache, _ = RecipeCache.objects.get_or_create(id=1)
    if recipe_cache.last_reset != today:
        updated = (
            RecipeCache.objects.filter(id=1)
            .exclude(last_reset=today)
            .update(recipes={}, last_reset=today)
        )
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
        if (
            vowel_count == 0
            or consonant_count == 0
            or len(text) > 30
            or len(text) == 1
            or len(text) > 9 * vowel_count
        ):
            return True
    return False


def build_cache_key(ingredients, exclude, tools):
    return "recipes:" + "|".join(
        [
            ",".join(sorted(i.lower() for i in ingredients)),
            ",".join(sorted(e.lower() for e in exclude)),
            ",".join(sorted(t.lower() for t in tools)),
        ]
    )


def search_recipes(user, ingredients, tools, exclude, limited):
    recipes, errors = [], []

    for tool in tools:
        if tool not in EQUIPMENT:
            errors.append(("tools", TOOL_ERROR.format(tool)))
    if limited:
        errors.append(("rate_limit", RATE_LIMIT_ERROR))

    if suspicious(ingredients):
        sus = SuspiciousRequest.objects.create(user=user, arguments=list(ingredients))
        if limited:
            sus.arguments.append("Hit rate limit")
            sus.save()
        return recipes, errors

    if not ingredients or errors:
        return recipes, errors

    key = build_cache_key(ingredients, exclude, tools)
    recipe_cache = get_recipe_cache()
    cached = recipe_cache.recipes.get(key)

    if cached is None:
        try:
            response = requests.get(
                API_URL,
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
                timeout=8,
            )
            response.raise_for_status()
            cached = [normalize(x) for x in response.json().get("results", [])]
        except (requests.RequestException, ValueError):
            errors.append(("upstream", UPSTREAM_ERROR))
            return [], errors

        for r in cached:
            Recipe.objects.update_or_create(
                id=r["id"],
                defaults={
                    "title": r["title"],
                    "image": r.get("image"),
                    "summary": r.get("summary"),
                    "instructions": r.get("instructions"),
                    "nutrients": r.get("nutrition"),
                    "source": r.get("source"),
                },
            )
        recipe_cache.recipes[key] = cached
        recipe_cache.save()

    ids = [r["id"] for r in cached]
    by_id = Recipe.objects.in_bulk(ids)
    recipes = [by_id[i] for i in ids if i in by_id]  # keep API ordering
    return recipes, errors


def get_steps(recipe):
    instructions = recipe.instructions or []
    if isinstance(instructions, list) and instructions:
        return instructions[0].get("steps", []) or []
    return []


def get_nutrients(recipe):
    data = recipe.nutrients or {}
    return data.get("nutrients", []) if isinstance(data, dict) else []


def is_saved(user, recipe):
    if not user.is_authenticated:
        return False
    from saved_recipe.models import SavedRecipe

    return SavedRecipe.objects.filter(user=user, source_recipe=recipe).exists()
