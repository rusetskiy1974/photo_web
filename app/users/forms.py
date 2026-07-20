from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm

from locations.models import Country, City
from .models import User, ClientProfile, PhotographerProfile
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

class ProfileEditForm(forms.ModelForm):
    avatar_file = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
        })
    )

    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("Your first name"),
        })
    )

    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("Your last name"),
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("Your phone"),
        })
    )

    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("Your address"),
        })
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "address",
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if phone and not phone.isdigit():
            raise forms.ValidationError(_("Phone number must contain only digits."))

        return phone

    def clean_avatar_file(self):
        avatar = self.cleaned_data.get("avatar_file")

        if avatar:
            max_size = MAX_AVATAR_SIZE_MB * 1024 * 1024

            if avatar.size > max_size:
                raise forms.ValidationError(
                    _(f"The maximum allowed file size is {MAX_AVATAR_SIZE_MB}MB.")
                )

        return avatar


class ClientProfileEditForm(forms.ModelForm):
    preferred_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label="Select country",
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "id_preferred_country"
        })
    )

    preferred_city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        empty_label="Select city",
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "id_preferred_city"
        })
    )

    notes = forms.CharField(
        label="Notes",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 4,
            "class": "form-control",
            "placeholder": "Add your preferences, ideas or special requests..."
        }),
        help_text="Optional notes for your future bookings."
    )

    class Meta:
        model = ClientProfile
        fields = (
            "preferred_country",
            "preferred_city",
            "notes",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "preferred_country" in self.data:
            try:
                country_id = int(self.data.get("preferred_country"))
                self.fields["preferred_city"].queryset = City.objects.filter(
                    country_id=country_id
                ).order_by("name_en")
            except (ValueError, TypeError):
                self.fields["preferred_city"].queryset = City.objects.none()

        elif self.instance and self.instance.preferred_country:
            self.fields["preferred_city"].queryset = City.objects.filter(
                country=self.instance.preferred_country
            ).order_by("name_en")

        else:
            self.fields["preferred_city"].queryset = City.objects.none()


class PhotographerProfileEditForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        label="About you",
        widget=forms.Textarea(attrs={
            "rows": 4,
            "class": "form-control",
            "placeholder": "Tell clients about yourself, your style and experience..."
        }),
        help_text="Describe your photography style and experience."
    )

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label="Select country",
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "id_country"
        }),
        help_text="Select country where the photographer works"
    )

    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        empty_label="Select city",
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "id_city"
        }),
        help_text="Select city where the photographer works"
    )

    experience_years = forms.IntegerField(
        required=False,
        label="Experience",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Years of experience"
        }),
        help_text="How many years have you been working as a photographer?"
    )

    price_per_hour = forms.DecimalField(
        required=False,
        label="Price per hour",
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your hourly rate"
        }),
        help_text="Your base hourly rate."
    )

    is_available = forms.BooleanField(
        label="Available for booking",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
        help_text="Enable if you are currently accepting bookings."
    )

    class Meta:
        model = PhotographerProfile
        fields = (
            "bio",
            "country",
            "city",
            "experience_years",
            "price_per_hour",
            "is_available",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "country" in self.data:
            try:
                country_id = int(self.data.get("country"))
                self.fields["city"].queryset = City.objects.filter(
                    country_id=country_id
                ).order_by("name_en")
            except (ValueError, TypeError):
                self.fields["city"].queryset = City.objects.none()

        elif self.instance and self.instance.country:
            self.fields["city"].queryset = City.objects.filter(
                country=self.instance.country
            ).order_by("name_en")

        else:
            self.fields["city"].queryset = City.objects.none()

        for name, field in self.fields.items():
            if name != "is_available":
                field.widget.attrs.update({"class": "form-control"})

            else:
                field.widget.attrs.update({"class": "form-check-input"})

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
