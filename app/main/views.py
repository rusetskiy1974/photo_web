from django.shortcuts import render

from blog.models import Blog
from .models import Portfolio, Review

from django.http import HttpResponse
# from goods.models import Categories


def index(request):
    portfolio_items = Portfolio.objects.all()
    blogs = Blog.objects.all()

    context = {
        'title': "Home",
        'content': "Фотостудія RMS",
        'portfolio_items': portfolio_items,
        'blogs': blogs,
        }
    return render(request, 'main/index.html', context=context)

def about(request):
    reviews = Review.objects.all()
    context = {
        'title': "About Me",
        'content': "About me",
        'reviews': reviews,
        }
    return render(request, 'main/about.html', context=context)

def typography(request) -> HttpResponse:
    context = {
        'title': "Typography",
        'content': "Typography",
    }
    return render(request, 'main/typography.html', context=context)

def contact(request) -> HttpResponse:
    context = {
        'title': "Contact",
        'content': "Contact",
    }
    return render(request, 'main/contact_me.html', context=context)
