from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import User
from django.utils.translation import gettext_lazy as _


MAX_AVATAR_SIZE_MB = 1

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="{% trans 'Username or Email' %}",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter username or email')
        })
    )

    password = forms.CharField(
        label="{% trans 'Password' %}",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter password')
        })
    )

    def clean_username(self):
        login = self.cleaned_data.get("username")
        User = get_user_model()

        try:
            user = User.objects.get(email__iexact=login)
            return user.username
        except User.DoesNotExist:
            return login


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your user name')
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your password')
    }))


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        (User.Role.PHOTOGRAPHER, 'Photographer'),
        (User.Role.CLIENT, 'Client'),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "address",
            "role",
            "password1",
            "password2",
        )

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your first name')
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your last name')
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Username')
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'example@domain.com'
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your phone')
    }))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your address')
    }))
    role = forms.ChoiceField(choices=ROLE_CHOICES,widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': _('Select role')
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': _('Enter password')
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': _('Repeat password')
    }))

    # Додамо приклад кастомної валідації для телефону
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email

class ProfileEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "address",
        )

    avatar_file = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control-file'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your first name')
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your last name')
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Username')
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'example@domain.com'
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your phone')
    }))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Your address')
    }))

    # Додамо ту ж кастомну валідацію для телефону
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        return phone

    def clean_avatar_file(self):
        avatar = self.cleaned_data.get('avatar_file')

        if avatar:
            max_size = MAX_AVATAR_SIZE_MB * 1024 * 1024  # перевести в байти
            if avatar.size > max_size:
                raise forms.ValidationError(f"The maximum allowed file size is {MAX_AVATAR_SIZE_MB}MB.")
        return avatar

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
