
from django.db import models
from cloudinary import uploader
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import logging

logger = logging.getLogger(__name__)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CLIENT = "client", "Client"
        PHOTOGRAPHER = "photographer", "Photographer"

    email = models.EmailField(unique=True, verbose_name='Email')  # ✅ Make email unique
    avatar = models.URLField(max_length=500, blank=True, null=True, verbose_name="Avatar")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Address')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, verbose_name='Role')

    is_email_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'

    def upload_image(self, file):
        """
        Завантажує зображення користувача на Cloudinary з постійним public_id.
        При кожному завантаженні файл буде перезаписано.
        """
        if not file:
            return

        try:
            result = uploader.upload(
                file,
                public_id=f"avatars/user_{self.id}",
                overwrite=True,
                folder=None,
                invalidate=True,
                use_filename=True,
                unique_filename=False,
                resource_type="image"
            )
            self.avatar = result.get("secure_url")
            self.save(update_fields=["avatar"])
            logger.info(f"Cloudinary upload result: {result}")
        except Exception as e:
            logger.error(f"Не вдалося завантажити аватар для користувача {self.username}: {e}")

    def __str__(self):
        return self.username

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_photographer(self):
        return self.role == self.Role.PHOTOGRAPHER

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT


class ClientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )

    preferred_city = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client profile"
        verbose_name_plural = "Client profiles"

    def __str__(self):
        return f"Client: {self.user.username}"


class PhotographerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="photographer_profile"
    )

    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    price_per_hour = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Photographer profile"
        verbose_name_plural = "Photographer profiles"

    def __str__(self):
        return f"Photographer: {self.user.username}"