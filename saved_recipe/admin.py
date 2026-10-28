from django.contrib import admin
from .models import SavedRecipe


@admin.register(SavedRecipe)
class SavedRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "meal_category",
        "is_favorite",
        "created_at",
    )
    list_filter = ("meal_category", "is_favorite")
    search_fields = ("name",)