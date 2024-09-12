from django import forms
from .models import Category, Service
from django.utils.text import slugify

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']  # Видаляємо поле slug із форми
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва категорії'}),
        }

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        if not instance.slug:  # Автоматична генерація slug, якщо поле порожнє
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
    

class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service
        fields = ['name', 'description', 'image', 'price', 'category', 'duration']  # Видаляємо поле slug із форми
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва послуги'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опис послуги'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ціна'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Тривалість'}),
        }

    def save(self, commit=True):
        instance = super(ServiceForm, self).save(commit=False)
        if not instance.slug:  # Автоматична генерація slug, якщо поле порожнє
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
