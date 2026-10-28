from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Input Your Message'}),
        }