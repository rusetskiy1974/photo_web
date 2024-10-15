from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from photo_app.models import Photo
from .forms import ProfileForm, UserLoginForm, UserRegistrationForm


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

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required





from django.shortcuts import render, redirect
from django.contrib import messages
from photo_app.models import Photo

@login_required
def handle_photos(request):
    if request.method == 'POST':
        # Отримуємо список вибраних фото з форми
        photo_ids = request.POST.get('photo_ids', '')  # Стягуємо всі ID вибраних фото як рядок
        if photo_ids:
            # Розділяємо рядок з ID на список чисел
            photo_ids = photo_ids.split(',')
            try:
                # Перетворюємо кожен елемент у список цілих чисел
                photo_ids = [int(photo_id) for photo_id in photo_ids]
                
                # Знаходимо відповідні фото
                selected_photos = Photo.objects.filter(id__in=photo_ids)
                
                # Обробка дій в залежності від кнопки
                action = request.POST.get('action')
                
                if action == 'publish':
                    selected_photos.update(is_public=True)
                    messages.success(request, f"{selected_photos.count()} photos were made public.")
                elif action == 'private':
                    selected_photos.update(is_public=False)
                    messages.success(request, f"{selected_photos.count()} photos were made private.")
                elif action == 'download':
                    # Логіка завантаження фото, якщо потрібно
                    messages.success(request, f"{selected_photos.count()} photos were prepared for download.")
                    
                return redirect('users:my_photos')  # Перенаправляємо на список фото після обробки
                
            except ValueError:
                messages.error(request, "Invalid photo IDs. Please try again.")  # Передаємо аргументи request і повідомлення
        else:
            messages.warning(request, "No photos were selected.")  # Тут також передаємо request
            
    return redirect('users:my_photos')  # Перенаправляємо на список фото в разі помилки


@login_required
def handle_photos(request):
    if request.method == 'POST':
        # Отримуємо список вибраних фото з форми
        selected_photo_ids = request.POST.get('selected_photo_ids', '')
        obj_page = request.POST.get('obj_page', '1')  # Отримуємо поточну сторінку або дефолтну сторінку 1
        
        if selected_photo_ids:
            # Розділяємо рядок з ID на список чисел
            selected_photo_ids = selected_photo_ids.split(',')
            try:
                # Перетворюємо кожен елемент у список цілих чисел
                selected_photo_ids = [int(photo_id) for photo_id in selected_photo_ids]
                
                # Знаходимо відповідні фото
                selected_photos = Photo.objects.filter(id__in=selected_photo_ids)
                
                # Обробка дій в залежності від кнопки
                action = request.POST.get('action')
                
                if action == 'publish':
                    selected_photos.update(is_public=True)
                    messages.success(request, f"{selected_photos.count()} photos were made public.")
                elif action == 'private':
                    selected_photos.update(is_public=False)
                    messages.success(request, f"{selected_photos.count()} photos were made private.")
                elif action == 'download':
                    # Логіка завантаження фото, якщо потрібно
                    messages.success(request, f"{selected_photos.count()} photos were prepared for download.")
                    
                # Повертаємо на ту саму сторінку пагінації
                return redirect(f"{reverse('users:my_photos')}?page={obj_page}")
            
            except ValueError:
                messages.error(request, "Invalid photo IDs. Please try again.")  # Передаємо аргументи request і повідомлення
        else:
            messages.warning(request, "No photos were selected.")  # Тут також передаємо request
    
    return redirect(f"{reverse('users:my_photos')}?page={obj_page}")  # Перенаправляємо на ту ж сторінку

    
# def google_login_auto_redirect(request):
#     # Додаткові дії, якщо потрібно
#     print("Перехоплено запит на Google Login")

#     # Викликаємо стандартне представлення для обробки Google OAuth2
#     return OAuth2LoginView.as_view()(request)

