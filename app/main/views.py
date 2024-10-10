from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from photo_app.models import Photo, Rating
from reviews.models import Review
from blog.models import Blog
from .models import Portfolio
from cloudinary import CloudinaryImage

from django.http import HttpResponse, JsonResponse
# from goods.models import Categories

class PortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'main/portfolio_detail.html'  # Шлях до вашого шаблону
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо поточний портфель
        portfolio = self.get_object()

        # Отримуємо всі фото, що прив'язані до портфоліо через поле ManyToMany
        portfolio_photos = portfolio.photos.all()

        # Створюємо URL з трансформацією для кожного фото
        photos_with_text = []
        for photo in portfolio_photos:
            url_with_text = CloudinaryImage(photo.public_id).build_url(transformation=[
                {'width': 500, 'crop': "scale"},
                {'color': "#FFFFFF80", 'overlay': {'font_family': "Times", 'font_size': 90, 'font_weight': "bold", 'text': "Photo RMS"}},
                {'flags': "layer_apply", 'gravity': "center", 'y': 20}
            ])
            photos_with_text.append({
                'photo': photo,
                'url_with_text': url_with_text
            })

        # Додаємо фото портфоліо до контексту
        context['photos_with_text'] = photos_with_text
        context['title'] = f'Фото для портфоліо: {portfolio.title}'



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

@login_required
def rate_photo(request, photo_id):
    """
    Обробляє POST-запит для оцінки фото.
    """
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))  # Отримуємо значення оцінки з POST-запиту

        # Перевіряємо, чи існує вже оцінка від цього користувача
        rating, created = Rating.objects.get_or_create(
            photo=photo, 
            user=request.user,
            defaults={'value': rating_value}
        )

        # Якщо оцінка вже існує, оновлюємо її
        if not created:
            rating.value = rating_value
            rating.save()

        return JsonResponse({
            'success': True,
            'message': 'Rating has been submitted successfully',
            'average_rating': photo.average_rating(),  # Повертаємо оновлений середній рейтинг
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)
