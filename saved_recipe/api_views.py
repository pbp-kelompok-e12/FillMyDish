from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import SavedRecipe
from .serializers import SavedRecipeSerializer


class SavedRecipeListAPIView(ListAPIView):
    serializer_class = SavedRecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedRecipe.objects.filter(
            user=self.request.user
        ).order_by("-created_at")