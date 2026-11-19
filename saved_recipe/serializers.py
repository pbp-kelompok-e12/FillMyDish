from rest_framework import serializers

from .models import SavedRecipe


class SavedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedRecipe
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "meal_category",
            "is_favorite",
        ]