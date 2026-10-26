from django.db import models
# Create your models here.
class Nutrient(models.Model):
    name = models.CharField(max_length=255)
    amount = models.FloatField()
    unit = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name}: {self.amount} {self.unit}"
    
class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)
    summary = models.TextField()
    nutrients = models.ManyToManyField(Nutrient, related_name="nutrient")
    instructions = models.JSONField()
    
class RecipeCache(models.Model):
    key = models.TextField(primary_key=True)
    recipes = models.ManyToManyField(Recipe, related_name="related_recipe")
    
    

    

    
    