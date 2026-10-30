from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Input Your Message'}),
        }
        error_messages = {
            'rating': {'required': 'Pilih rating terlebih dahulu.'},
        }