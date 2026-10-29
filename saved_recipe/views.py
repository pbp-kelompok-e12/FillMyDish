from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import SavedRecipe
from .forms import SavedRecipeCreateForm
from django.utils.html import strip_tags
from recipefinder.models import Recipe

# READ: Menampilkan resep tersimpan
@login_required(login_url="/login")
def saved_recipe_page(request):

    recipes = SavedRecipe.objects.filter(
        user=request.user
    ).order_by("-created_at")

    search_query = request.GET.get("q", "").strip()
    current_category = request.GET.get("category", "all")

    if current_category != "all":
        recipes = recipes.filter(
            meal_category=current_category
        )

    if search_query:
        recipes = recipes.filter(
            name__icontains=search_query
        )

    categories = [
        {"value": "all", "label": "All"},
        {"value": "breakfast", "label": "Breakfast"},
        {"value": "lunch", "label": "Lunch"},
        {"value": "dinner", "label": "Dinner"},
        {"value": "snack", "label": "Snack"},
    ]

    mealplan_draft = request.session.get("mealplan_draft")
    draft_recipe_ids = (
        mealplan_draft.get("recipe_ids", [])
        if mealplan_draft
        else []
    )

    return render(request, "saved_recipe/saved_recipe.html", {
        "recipes": recipes,
        "categories": categories,
        "search_query": search_query,
        "current_category": current_category,
        "mealplan_draft": mealplan_draft,
        "draft_recipe_ids": draft_recipe_ids,
    })


# UPDATE: Favorite dan Meal Category
@login_required(login_url="/login")
@require_POST
def update_saved_recipe(request, pk):

    recipe = get_object_or_404(
        SavedRecipe,
        pk=pk,
        user=request.user
    )

    category = request.POST.get("meal_category", "")
    favorite = request.POST.get("is_favorite") == "true"

    valid_categories = [
        choice[0] for choice in SavedRecipe.CATEGORY_CHOICES
    ]

    if category not in valid_categories:
        return JsonResponse(
            {"error": "Invalid meal category"},
            status=400
        )

    recipe.meal_category = category
    recipe.is_favorite = favorite
    recipe.save(update_fields=["meal_category", "is_favorite"])

    return JsonResponse({
        "success": True,
        "category": recipe.get_meal_category_display(),
        "is_favorite": recipe.is_favorite,
    })


# DELETE: Menghapus resep tersimpan
@login_required(login_url="/login")
@require_POST
def delete_saved_recipe(request, pk):

    recipe = get_object_or_404(
        SavedRecipe,
        pk=pk,
        user=request.user
    )

    recipe.delete()

    return JsonResponse({"success": True})


# CREATE: Dipanggil dari halaman rekomendasi AI

@login_required(login_url="/login")
@require_POST
def create_saved_recipe(request):

    # Jika tombol berasal dari halaman Details
    if "recipe_id" in request.POST:
        recipe_id = request.POST.get("recipe_id", "").strip()

        if not recipe_id.isdecimal():
            return HttpResponseBadRequest("Invalid recipe ID")

        # Ambil resep asli dari database
        source = get_object_or_404(
            Recipe,
            pk=int(recipe_id)
        )

        # Simpan jika belum pernah disimpan user ini
        SavedRecipe.objects.get_or_create(
            user=request.user,
            source_recipe=source,
            defaults={
                "name": source.title[:200],
                "description": strip_tags(source.summary or ""),
                "image_url": source.image or "",
            },
        )

        return redirect("saved_recipe")

    # Pertahankan fitur Create lama
    form = SavedRecipeCreateForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest(
            form.errors.as_json()
        )

    recipe = form.save(commit=False)
    recipe.user = request.user
    recipe.save()

    return redirect("saved_recipe")


