
from django.db import models
from django.conf import settings


class SavedRecipe(models.Model):

    CATEGORY_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
        ("uncategorized", "Uncategorized"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_recipes"
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    image_url = models.URLField(blank=True)

    meal_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="uncategorized"
    )

    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
