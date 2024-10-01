from django.db import models

from users.models import User
from photo_app.models import Photo

class Category(models.TextChoices):
    PORTRAIT = 'PT', 'Portrait'
    LANDSCAPE = 'LS', 'Landscape'
    WILDLIFE = 'WL', 'Wildlife'
    ARCHITECTURE = 'AR', 'Architecture'
    FASHION = 'FS', 'Fashion'


class Portfolio(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.PORTRAIT,
    )
    photographer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    photos = models.ManyToManyField(Photo, related_name='portfolios')

    class Meta:
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return self.title or "Portfolio without title"
    


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True, null=False)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

       
