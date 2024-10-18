from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from users.models import User

from enum import Enum

class PhotographyCategory(Enum):
    WEDDING = "Wedding Photography"
    FAMILY_CHILDREN = "Family and Children Photography"
    PORTRAIT = "Portrait Photography"
    BUSINESS_CORPORATE = "Business and Corporate Photography"
    FASHION_MODEL = "Model and Fashion Photography"
    EVENT = "Event Photography"
    ARCHITECTURAL_INTERIOR = "Architectural and Interior Photography"
    FOOD = "Food Photography"
    NUDE_ARTISTIC = "Nude or Artistic Photography"
    PHOTOJOURNALISM_DOCUMENTARY = "Photojournalism or Documentary Photography"
    NATURE_LANDSCAPE = "Nature and Landscape Photography"
    SPORTS = "Sports Photography"
    AVIATION_AUTOMOTIVE = "Aviation or Automotive Photography"
    PET = "Pet Photography"
    PANORAMIC_360 = "360-Degree and Panoramic Photography"
    STUDIO = "Studio Photography"
    CREATIVE_CONCEPTUAL = "Creative or Conceptual Photography"

    @classmethod
    def choices(cls):
        return [(category.name, category.value) for category in cls]


class Category(models.Model):
    name = models.CharField(
        max_length=150, 
        unique=True, 
        choices=PhotographyCategory.choices(),  # Використовуємо choices з enum
        verbose_name='Назва'
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорію'
        verbose_name_plural = 'Категорії'
        ordering = ("id",)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Назва')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Опис')
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name='Зображення')
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name='Ціна')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Категорія')
    duration = models.DurationField(verbose_name='Тривалість')
    created_by = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Виконавець')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    class Meta:
        db_table = 'services'
        verbose_name = 'Послуга'
        verbose_name_plural = 'Послуги'
        ordering = ("id",)

    def __str__(self):
        return f'{self.name} тривалість - {self.duration}'

    def get_absolute_url(self):
        return reverse("catalog:service", kwargs={"service_slug": self.slug})

    def display_id(self):
        return f"{self.id:05d}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            queryset = Service.objects.filter(slug=original_slug).exclude(pk=self.pk)
            counter = 1
            while queryset.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                queryset = Service.objects.filter(slug=self.slug).exclude(pk=self.pk)
        super(Service, self).save(*args, **kwargs)