from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'text']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва відгуку'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Текст відгуку'}),
        }