from django import forms
from .models import SavedRecipe


class SavedRecipeCreateForm(forms.ModelForm):
    class Meta:
        model = SavedRecipe
        fields = ["name", "description", "image_url"]