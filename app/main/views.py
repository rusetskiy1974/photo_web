from django.shortcuts import render
from django.views.generic import DetailView

from reviews.models import Review
from blog.models import Blog
from .models import Portfolio

from django.http import HttpResponse
# from goods.models import Categories

class PortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'main/portfolio_detail.html'  # Вкажіть правильний шлях до вашого шаблону
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio'] = Portfolio.objects.get(pk=self.kwargs['pk'])
        return context

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
