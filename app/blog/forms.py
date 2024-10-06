from django import forms
from .models import Blog, Post

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'description'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва блогу'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опис блогу'}),
        }
        
        

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content'] 

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва поста'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Текст поста'}),
        }