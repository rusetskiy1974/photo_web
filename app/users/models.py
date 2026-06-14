
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
    def is_photographer(self):
        return self.role == self.Role.PHOTOGRAPHER

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT