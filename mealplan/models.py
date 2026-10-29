from django.db import models
from FillMyDish.models import User

class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class MealPlanItem(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='items')
    recipe = models.ForeignKey("saved_recipe.SavedRecipe", on_delete=models.CASCADE, related_name="meal_plan_items",)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.recipe.name} di {self.meal_plan.title} (Urutan: {self.order})"