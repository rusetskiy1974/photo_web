import logging

from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView

from cloudinary import CloudinaryImage

from photo_app.models import Photo
from .forms import (
    ProfileEditForm,
    UserRegistrationForm,
    EmailOrUsernameAuthenticationForm,
    CustomPasswordChangeForm,
)
from .tokens import account_activation_token
from .utils import download_photos_as_zip as download_photos

logger = logging.getLogger(__name__)

User = get_user_model()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode((uidb64)))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        return render (request, 'users/activations_succes.html')
    else:
        return render(request, 'users/activations_invalid.html')

def google_register_client(request):
    request.session["google_flow"] = "register"
    request.session["google_role"] = User.Role.CLIENT
    return redirect("/accounts/google/login/")


def google_register_photographer(request):
    request.session["google_flow"] = "register"
    request.session["google_role"] = User.Role.PHOTOGRAPHER
    return redirect("/accounts/google/login/")


def google_login(request):
    request.session["google_flow"] = "login"
    request.session.pop("google_role", None)
    return redirect("/accounts/google/login/")



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


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registrations.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        # перший користувач = admin
        if not User.objects.exists():
            user.role = User.Role.ADMIN
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True  # щоб адмін не чекав email
        else:
            user.is_active = False  # для всіх інших підтвердження пошти
        user.save()

        # якщо не адмін — відправляємо лист активації
        if user.role != User.Role.ADMIN:
            current_site = get_current_site(self.request)

            message = render_to_string('users/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            email = EmailMessage(
                'Підтвердження email',
                message,
                to=[user.email],
            )
            email.send()

        messages.success(
            self.request,
            "Реєстрація успішна. Перевірте пошту."
        )

        return redirect(self.success_url)


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
    template_name = 'users/cabinet.html'
    context_object_name = 'user_obj'

    def get_template_names(self):
        if self.request.user.role == "photographer":
            return ['users/cabinet.html']
        return ['users/cabinet.html']

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'cabinet'
        # context['active_tab'] = 'profile'
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
        messages.success(self.request, "Profile successfully updated")
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
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:password_change_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'cabinet'
        context['active_tab'] = 'profile'
        return context


@login_required
def password_change_done(request):
    context = {
        'active_page': 'cabinet',
        'active_tab': 'profile',
    }
    return render(request, 'users/password_change_done.html', context)