import os

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.utils.http import url_has_allowed_host_and_scheme
import zipfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.views import PasswordResetView, LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
import requests
from traitlets import Instance
from cloudinary import CloudinaryImage
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, UpdateView
from photo_app.models import Photo
from .models import User
from .utils import download_photos_as_zip as download_photos
from .forms import ProfileEditForm, UserLoginForm, UserRegistrationForm, EmailOrUsernameAuthenticationForm, \
    CustomPasswordChangeForm
from allauth.socialaccount.providers.google.views import OAuth2LoginView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login



@csrf_exempt
def sign_in_with_google(request):
    return render(request, 'users/sign_in_with_google.html')

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    token = request.POST['credential']
    if not token:
        return HttpResponse("Missing token", status=400)


    try:
        user_data = id_token.verify_oauth2_token(
            token, google_requests.Request(), os.environ['GOOGLE_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    email = user_data.get("email")
    first_name = user_data.get("given_name", "")
    last_name = user_data.get("family_name", "")
    picture = user_data.get("picture", "")
    User = get_user_model()
    user, created = User.objects.get_or_create(email=email, defaults={
        "username": email,  # or generate a unique one
        "first_name": first_name,
        "last_name": last_name,
        "role": "Client",
    })
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    # if picture and (created or not user.image):
    #     user.image = picture  # Only works if you later handle it as a URL or download it to a file
    #     user.save(update_fields=["image"])
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth_login(request, user)

    return redirect('main:index')

def sign_out(request):
    del request.session['user_data']
    return redirect('users:profile')


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    # html_email_template_name = 'users/password_reset_email.html'
    # success_message = "An email with instructions to reset your password has been sent to %(email)s."
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class CustomLoginView(LoginView):
    form_class = EmailOrUsernameAuthenticationForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# def login(request):
#     if request.method == "POST":
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST["username"]
#             password = request.POST["password"]
#             user = auth.authenticate(username=username, password=password)
#             if user:
#                 auth.login(request, user)
#                 messages.success(request, f"{username}, Ви зайшли в аккаунт")
#
#                 next_url = request.POST.get('next')
#                 if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
#                     return redirect(next_url)
#                 return redirect("main:index")
#     else:
#         form = UserLoginForm()
#
#     context = {
#         "title": "Home - Логін",
#         "form": form,
#     }
#     return render(request, "users/login.html", context=context)


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registrations.html'
    success_url = reverse_lazy('users:login')


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user_obj'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'profile'
        context['active_page'] = 'cabinet'
        context['active_menu'] = 'main'
        return context

class UserCabinetView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user_obj'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'cabinet'
        context['active_tab'] = 'profile'
        context['active_menu'] = 'main'
        return context

class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        self.object = form.save()
        avatar_file = form.cleaned_data.get('avatar_file')
        if avatar_file:
            self.object.upload_image(avatar_file)
        return HttpResponseRedirect(self.get_success_url())
        # response = super().form_valid(form)
        # avatar_file = self.request.FILES.get('avatar_file')
        # if avatar_file:
        #     self.object.upload_image(avatar_file)
        # return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'profile'
        context['active_page'] = 'cabinet'
        context['active_menu'] = 'main'
        return context














# def registration(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#             user = form.instance
#             user.backend = 'django.contrib.auth.backends.ModelBackend'
#             auth.login(request, user)
#             messages.success(request, f"{user.username}, Ви успішно зареєструвалися, заходьте в аккаунт")
#             return HttpResponseRedirect(reverse("users:login"))
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field.capitalize()}: {error}")
#     else:
#         form = UserRegistrationForm()
#     print("errors=",form.errors)
#
#     context = {
#         "title": "Home - Реєстрація",
#         "form": form,
#     }
#     return render(request, "users/registrations.html",context=context)


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
    photos_with_overlay = []
    for photo in my_photos:
        url_with_text = CloudinaryImage(photo.public_id).build_url(transformation=[
  {'width': 500, 'crop': "scale"},
  {'color': "#FFFFFF80", 'overlay': {'font_family': "Times", 'font_size': 90, 'font_weight': "bold", 'text': "Photo RMS"}},
  {'flags': "layer_apply", 'gravity': "center", 'y': 20}
  ])
        # Apply transparent image overlay to all public photos
        url = CloudinaryImage(photo.public_id).build_url(transformation=[
            {'width': 500, 'crop': 'scale'},  # Scale image
            {'overlay': 'logo', 'opacity': 50, 'width': 0.55, 'flags': 'relative'}
        ])
        photos_with_text.append({
            'photo': photo,
            'url_with_text': url_with_text
        })
        photos_with_overlay.append({
            'photo': photo,
            'url_with_text': url
        })
    context = {
        'title': 'My photos',
        'photos_with_text': photos_with_overlay,
        'active_page': 'cabinet',
        'active_tab': 'gallery',
        
    }
    

    return render(request, 'users/my_photos.html', context)

@login_required
def add_review(request):
    user_photos = Photo.objects.filter(owner=request.user.id)

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = []
    for photo in user_photos:
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

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('account:password_change_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'change_password'
        context['active_menu'] = 'main'
        return context