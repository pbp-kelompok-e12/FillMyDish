from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

def saved_recipe_page(request):
    recipes = [
        {
            "name": "Nasi Goreng",
            "description": "Nasi goreng dengan telur.",
            "category": "Breakfast",
            "is_favorite": True,
            "image": "img/nasgor-1.png",
        },
        {
            "name": "Ayam Bakar",
            "description": "Ayam bakar bumbu kecap.",
            "category": "Lunch",
            "is_favorite": False,
            "image": "",
        },
        {
            "name": "Pancake",
            "description": "Pancake lembut dan manis.",
            "category": "Snack",
            "is_favorite": True,
            "image": "",
        },
        {
            "name": "Sup Ayam",
            "description": "Sup ayam dengan sayuran.",
            "category": "Dinner",
            "is_favorite": False,
            "image": "",
        },
    ]

    categories = [
        {"value": "all", "label": "All"},
        {"value": "breakfast", "label": "Breakfast"},
        {"value": "lunch", "label": "Lunch"},
        {"value": "dinner", "label": "Dinner"},
        {"value": "snack", "label": "Snack"},
    ]

    search_query = request.GET.get("q", "").strip()
    current_category = request.GET.get("category", "all").lower()

    if current_category != "all":
        recipes = [
            recipe for recipe in recipes
            if recipe["category"].lower() == current_category
        ]

    if search_query:
        recipes = [
            recipe for recipe in recipes
            if search_query.lower() in recipe["name"].lower()
        ]

    context = {
        "recipes": recipes,
        "categories": categories,
        "search_query": search_query,
        "current_category": current_category,
    }

    return render(
        request,
        "saved_recipe/saved_recipe.html",
        context
    )

