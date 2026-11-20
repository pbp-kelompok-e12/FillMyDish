from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipefinder.models import Recipe

from .serializers import (
    RecipeDetailSerializer,
    RecipeListSerializer,
    RecipeSearchParamsSerializer,
)
from .services import search_recipes


class RecipeSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="ip", rate="5/m", block=False, group="recipe-search"))
    def get(self, request):
        params = RecipeSearchParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        ingredients = params.validated_data["ingredients"]
        tools = params.validated_data["tools"]
        exclude = params.validated_data["exclude"]

        recipes, errors = search_recipes(
            request.user, ingredients, tools, exclude,
            limited=getattr(request, "limited", False),
        )

        if errors:
            grouped = {}
            for code, message in errors:
                grouped.setdefault(code, []).append(message)
            if "rate_limit" in grouped:
                code = status.HTTP_429_TOO_MANY_REQUESTS
            elif "tools" in grouped:
                code = status.HTTP_400_BAD_REQUEST
            else:
                code = status.HTTP_502_BAD_GATEWAY
            return Response({"errors": grouped}, status=code)

        data = RecipeListSerializer(recipes, many=True).data
        return Response({"ingredients": ingredients, "count": len(data), "recipes": data})


class RecipeDetailAPIView(RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    lookup_url_kwarg = "recipe_id"
    lookup_field = "pk"
    permission_classes = [AllowAny]
