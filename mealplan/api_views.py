from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import MealPlan
from .serializers import MealPlanSerializer


class MealPlanListAPIView(ListAPIView):
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealPlan.objects.filter(
            user=self.request.user
        ).order_by("-created_at")