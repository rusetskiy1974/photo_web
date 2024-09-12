from django.shortcuts import render
from .models import Portfolio

from django.http import HttpResponse
# from goods.models import Categories


def index(request):
    portfolio_items = Portfolio.objects.all()

    context = {
        'title': "Home",
        'content': "Фотостудія RMS",
        'portfolio_items': portfolio_items
        }
    return render(request, 'main/index.html', context=context)

def about(request):
    context = {
        'title': "About Me",
        'content': "About me",
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
