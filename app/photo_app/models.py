from enum import IntEnum
from django.db import models
from cloudinary import uploader

from users.models import User

class RatingChoices(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.replace('_', ' ').title()) for choice in cls]


class Photo(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=255, blank=True, verbose_name="Cloudinary public_id")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="Cloudinary Image URL")
    owner = models.ForeignKey(User,  
        on_delete=models.CASCADE,   
        null=True,   
        blank=True,   
        related_name='photos',  # Це дозволяє доступ до фотографій через user.photos.all()
    )
    is_public = models.BooleanField(default=False, verbose_name="Публічне фото")
    

    def upload_image(self, file):
        """
        Завантажує зображення на Cloudinary і зберігає його public_id та URL.
        """
        if file:
            result = uploader.upload(file)
            self.public_id = result.get('public_id')
            self.image_url = result.get('secure_url')
            self.save()

    def delete(self, *args, **kwargs):
        if self.public_id:
            uploader.destroy(self.public_id)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Photo <{self.title}:{self.public_id}>"
    
    def average_rating(self):
        ratings = self.ratings.all()  # Отримуємо всі оцінки, пов'язані з цим фото
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0  # Якщо оцінок немає, повертаємо 0


class Rating(models.Model):
    photo = models.ForeignKey(Photo, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    value = models.IntegerField(choices=RatingChoices.choices()) 

    class Meta:
        unique_together = ('photo', 'user')

    def __str__(self):
        return f"Rating {self.value} by {self.user} for {self.photo.title}"