from typing import Any

from django.db import models
from django.urls import reverse

from users.models import User
from photo_app.models import Photo

class Category(models.TextChoices):
    PORTRAIT = 'PT', 'Portrait'
    LANDSCAPE = 'LS', 'Landscape'
    WILDLIFE = 'WL', 'Wildlife'
    ARCHITECTURE = 'AR', 'Architecture'
    FASHION = 'FS', 'Fashion'

    # @property
    # def choices(self) -> Any:


    @classmethod
    def get_image(cls, category_code):
        images = {
            cls.PORTRAIT: 'categories/portrait.jpg',
            cls.LANDSCAPE: 'categories/landscape.jpg',
            cls.WILDLIFE: 'categories/wildlife.jpg',
            cls.ARCHITECTURE: 'categories/architecture.jpg',
            cls.FASHION: 'categories/fashion.jpg',
        }
        return images.get(category_code, 'categories/default.jpg')  # Повертає зображення або за замовчуванням


class Portfolio(models.Model):
    create_time: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    title: models.CharField = models.CharField("Title (optional)", max_length=200, blank=True)
    description: models.TextField = models.TextField(blank=True, null=True)
    category: models.CharField = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.PORTRAIT,
    )
    photos: models.ManyToManyField = models.ManyToManyField(Photo, related_name='portfolios', blank=True)

    class Meta:
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return self.title or "Portfolio without title"
    
    def get_category_image(self):
        return Category.get_image(self.category)

    def get_absolute_url(self):
        return reverse('main:portfolio_detail', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = Category(self.category).label
        super().save(*args, **kwargs)