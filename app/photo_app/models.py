from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary import uploader
from .utils.image_validator import file_validation

class Photo(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=255, blank=True)

    def delete(self, *args, **kwargs):
        if self.public_id:
            uploader.destroy(self.public_id)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Photo <{self.title}:{self.public_id}>"
