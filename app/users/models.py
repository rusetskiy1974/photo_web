from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from photo_app.utils.image_validator import file_validation


class Role(models.TextChoices):
    MASTER = 'Master'
    CLIENT = 'Client'

class User(AbstractUser):
    image = models.ImageField(upload_to='users_images',
                               blank=True,
                               null=True,
                               verbose_name='Аватар',
                               validators=[file_validation, FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Адреса')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT, verbose_name='Роль')
    

    class Meta:
        db_table = 'user'
      
        

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"