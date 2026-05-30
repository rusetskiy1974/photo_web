from typing import Any

from django.db import models
from django.urls import reverse

from users.models import User
from photo_app.models import Photo

class Category(models.TextChoices):
    WEDDING = 'WD', 'Wedding'
    FAMILY = 'FM', 'Family'
    LOVE_STORY = 'LV', 'Love Story'
    PORTRAIT = 'PT', 'Portrait'
    CHILDREN = 'CH', 'Children'
    MATERNITY = 'MT', 'Maternity'
    BUSINESS = 'BS', 'Business Portrait'
    EVENT = 'EV', 'Event'
    FASHION = 'FS', 'Fashion'
    LANDSCAPE = 'LS', 'Landscape'
    ARCHITECTURE = 'AR', 'Architecture'
    WILDLIFE = 'WL', 'Wildlife'
    OTHER = 'OT', 'Other'



    # @property
    # def choices(self) -> Any:
    #     return


    @classmethod
    def get_image(cls, category_code):
        images = {
            cls.WEDDING: 'categories/wedding.jpg',
            cls.FAMILY: 'categories/family.jpg',
            cls.LOVE_STORY: 'categories/love_story.jpg',
            cls.PORTRAIT: 'categories/portrait.jpg',
            cls.CHILDREN: 'categories/children.jpg',
            cls.MATERNITY: 'categories/maternity.jpg',
            cls.BUSINESS: 'categories/business.jpg',
            cls.EVENT: 'categories/event.jpg',
            cls.FASHION: 'categories/fashion.jpg',
            cls.LANDSCAPE: 'categories/landscape.jpg',
            cls.ARCHITECTURE: 'categories/architecture.jpg',
            cls.WILDLIFE: 'categories/wildlife.jpg',
            cls.OTHER: 'categories/default.jpg',



        }
        return images.get(category_code, 'categories/default.jpg')  # Повертає зображення або за замовчуванням


class Portfolio(models.Model):
    create_time: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    title: models.CharField = models.CharField("Title (optional)", max_length=200, blank=True)
    description: models.TextField = models.TextField(blank=True, null=True)
    category: models.CharField = models.CharField(
        max_length=2,
        choices=Category.choices,
        # default=Category.PORTRAIT,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    photos: models.ManyToManyField = models.ManyToManyField(Photo, related_name='portfolios', blank=True)

    class Meta:
        verbose_name_plural = "Portfolios"
        ordering = ['category']


    def __str__(self):
        return self.title or self.get_category_display()

    @property
    def category_name(self):
        return self.get_category_display()
    
    def get_category_image(self):
        return Category.get_image(self.category)

    def get_absolute_url(self):
        return reverse('main:portfolio_detail', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.get_category_display()
        super().save(*args, **kwargs)