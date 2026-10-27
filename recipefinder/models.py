from django.db import models
# Create your models here.

class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)
    summary = models.TextField()
    nutrients = models.JSONField(default=dict)
    instructions = models.JSONField(default=dict)
    
class RecipeCache(models.Model):
    id = models.IntegerField(primary_key=True)
    recipes = models.JSONField(default=dict)
    
    

    

    
    