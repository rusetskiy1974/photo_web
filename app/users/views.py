import io
import zipfile
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, redirect, render
from django.urls import reverse
import requests
from traitlets import Instance
from cloudinary import CloudinaryImage

from photo_app.models import Photo
from .utils import download_photos_as_zip as download_photos
from .forms import ProfileForm, UserLoginForm, UserRegistrationForm
from allauth.socialaccount.providers.google.views import OAuth2LoginView


def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Ви зайшли в аккаунт")

                if request.POST.get('next', None):
                    return HttpResponseRedirect(request.POST.get('next'))
                
                return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserLoginForm()
         
    context = {
        "title": "Home - Логін",
        "form": form,
    }
    return render(request, "users/login.html", context=context)


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            messages.success(request, f"{user.username}, Ви успішно зареєструвалися, заходьте в аккаунт")
            return HttpResponseRedirect(reverse("users:login"))
    else:
        form = UserRegistrationForm()
    print("errors=",form.errors) 

    context = {
        "title": "Home - Реєстрація",
        "form": form,
    }
    return render(request, "users/registrations.html",context=context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(
            data=request.POST, instance=request.user, files=request.FILES
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профайл успішно оновлено")
            return HttpResponseRedirect(reverse("users:profile"))
        
    else:
        form = ProfileForm(instance=request.user)

    context = {
        "title": "Home - Профіль",
        "form": form,
    }
    return render(request, "users/edit_profile.html", context=context)

@login_required
def profile(request):
    context = {
        "title": "Home - Мій профіль",
        "user": request.user,  # Поточний користувач
    }
    return render(request, "users/profile.html", context=context)

@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Ви вийшли з аккаунту")
    auth.logout(request)
    return redirect(reverse("main:index"))

@login_required
def my_photos(request):
    my_photos = Photo.objects.filter(owner=request.user.id)

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = []
    for photo in my_photos:
        url_with_text = CloudinaryImage(photo.public_id).build_url(transformation=[
  {'width': 500, 'crop': "scale"},
  {'color': "#FFFFFF80", 'overlay': {'font_family': "Times", 'font_size': 90, 'font_weight': "bold", 'text': "Photo RMS"}},
  {'flags': "layer_apply", 'gravity': "center", 'y': 20}
  ])
        photos_with_text.append({
            'photo': photo,
            'url_with_text': url_with_text
        })
    context = {
        'title': 'My photos',
        'photos_with_text': photos_with_text,
        
    }
    

    return render(request, 'users/my_photos.html', context)

@login_required
def add_review(request):
    my_photos = Photo.objects.filter(owner=request.user.id)

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = []
    for photo in my_photos:
        url_with_text = CloudinaryImage(photo.public_id).build_url(transformation=[
  {'width': 500, 'crop': "scale"},
  {'color': "#FFFFFF80", 'overlay': {'font_family': "Times", 'font_size': 90, 'font_weight': "bold", 'text': "Photo RMS"}},
  {'flags': "layer_apply", 'gravity': "center", 'y': 20}
  ])
        photos_with_text.append({
            'photo': photo,
            'url_with_text': url_with_text
        })
    context = {
        'title': 'My photos',
        'photos_with_text': photos_with_text,
        
    }
    
    return render(request, 'users/my_photos.html', context)

@login_required
def handle_photos(request):
    photo_ids = request.POST.getlist('photo_ids')
    
    if not photo_ids:
        messages.warning(request, "Не вибрано жодного фото.")
        return HttpResponseRedirect(reverse('users:my_photos'))

    photos = get_list_or_404(Photo, id__in=photo_ids, owner=request.user)
    
    action = request.POST.get('action')

    if action == 'publish':
        # Робимо фото публічними
        for photo in photos:
            photo.is_public = True
            photo.save()
        messages.success(request, "Вибрані фото стали публічними.")
        return HttpResponseRedirect(reverse('users:my_photos'))
    
    elif action == 'download':
        
        return download_photos(photos)

    else:
        messages.error(request, "Невідома дія.")
        return HttpResponseRedirect(reverse('users:my_photos'))

@login_required
def add_photo_public(request):
    photo_ids = request.GET.getlist('photo_ids')
    
    if not photo_ids:
        messages.warning(request, "Не вибрано жодного фото.")
        return HttpResponseRedirect(reverse('users:my_photos'))
    
    # Отримуємо всі фото за їх id
    photos = get_list_or_404(Photo, id__in=photo_ids, owner=request.user)
    
    if request.method == 'POST':
        # Для кожного фото встановлюємо значення поля is_public
        for photo in photos:
            photo.is_public = True  # Встановлюємо статус публічності
            photo.save()  # Зберігаємо зміни
            
        messages.success(request, "Вибрані фото стали публічними.")
        return HttpResponseRedirect(reverse('users:my_photos'))

    return render(request, 'users/my_photos.html', {'photos': photos})
    
# def google_login_auto_redirect(request):
#     # Додаткові дії, якщо потрібно
#     print("Перехоплено запит на Google Login")

#     # Викликаємо стандартне представлення для обробки Google OAuth2
#     return OAuth2LoginView.as_view()(request)

