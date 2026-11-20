from rest_framework import serializers

from .models import Recipe
from .services import get_nutrients, get_steps, is_saved, split_csv


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "title", "image", "summary", "source"]
        read_only_fields = fields


class RecipeDetailSerializer(serializers.ModelSerializer):
    nutrients = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    already_saved = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ["id", "title", "image", "summary", "source", "nutrients", "steps", "already_saved"]
        read_only_fields = fields

    def get_nutrients(self, obj):
        return get_nutrients(obj)

    def get_steps(self, obj):
        return get_steps(obj)

    def get_already_saved(self, obj):
        request = self.context.get("request")
        return bool(request) and is_saved(request.user, obj)


class RecipeSearchParamsSerializer(serializers.Serializer):
    ingredients = serializers.CharField(required=False, allow_blank=True, default="")
    tools = serializers.CharField(required=False, allow_blank=True, default="")
    exclude = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_ingredients(self, value):
        return split_csv(value)

    def validate_tools(self, value):
        return split_csv(value)

    def validate_exclude(self, value):
        return split_csv(value)
