from django.db import models
from django.urls import reverse

from photo_app.models import Photo

class Category(models.TextChoices):
    PORTRAIT = 'PT', 'Portrait'
    LANDSCAPE = 'LS', 'Landscape'
    WILDLIFE = 'WL', 'Wildlife'
    ARCHITECTURE = 'AR', 'Architecture'
    FASHION = 'FS', 'Fashion'

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

    @classmethod
    def get_full_name(cls, category_code):
        names = {
            cls.PORTRAIT: 'Portrait',
            cls.LANDSCAPE: 'Landscape',
            cls.WILDLIFE: 'Wildlife',
            cls.ARCHITECTURE: 'Architecture',
            cls.FASHION: 'Fashion',
        }
        return names.get(category_code, 'Unknown Category')  # Повертає повну назву категорії


class Portfolio(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.PORTRAIT,
    )
    photos = models.ManyToManyField(Photo, related_name='portfolios', blank=True)

    class Meta:
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return self.title or "Portfolio without title"

    def get_category_image(self):
        return Category.get_image(self.category)

    def get_absolute_url(self):
        return reverse('main:portfolio_detail', args=[self.id])

    def save(self, *args, **kwargs):
        # Якщо title або description не задано, встановлюємо їх за замовчуванням
        if not self.title:
            self.title = Category.get_full_name(self.category)
        if not self.description:
            self.description = f"This portfolio contains {self.title} photos."
        super().save(*args, **kwargs)  # Викликаємо метод з батьківського класу
