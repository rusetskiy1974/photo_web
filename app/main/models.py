from django.core.files.uploadedfile import UploadedFile
from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary import uploader
from django.core.exceptions import ValidationError

from users.models import User

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10mb


def file_validation(file):
    if not file:
        raise ValidationError("No file selected.")

    if isinstance(file, UploadedFile):
        if file.size > FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise ValidationError("File shouldn't be larger than 10MB.")


class Portfolio(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', validators=[file_validation])

    def delete(self, *args, **kwargs):
        if self.image:
            public_id = self.image.public_id
            uploader.destroy(public_id)
        super().delete(*args, **kwargs)

    """ Informative name for model """

    def __unicode__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s:%s>" % (self.title, public_id)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True, null=False)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

       
