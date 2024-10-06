from django.forms import ModelForm

import cloudinary
import hashlib
# Next two lines are only used for generating the upload preset sample name
from cloudinary.compat import to_bytes
from cloudinary.forms import CloudinaryJsFileField, CloudinaryUnsignedJsFileField

from users.models import User, Role
from .models import Photo
from django import forms
from .utils.image_validator import file_validation


class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = '__all__'


class PhotoDirectForm(PhotoForm):
    image = CloudinaryJsFileField(
        attrs={'style': "margin-top: 30px"},
        options={
            'tags': "directly_uploaded",
            'crop': 'limit', 'width': 1000, 'height': 1000,
            'eager': [{'crop': 'fill', 'width': 150, 'height': 100}]
        })


class PhotoUnsignedDirectForm(PhotoForm):
    upload_preset_name = "sample_" + hashlib.sha1(
        to_bytes(cloudinary.config().api_key + cloudinary.config().api_secret)).hexdigest()[0:10]
    image = CloudinaryUnsignedJsFileField(upload_preset_name)


class UploadOwner(forms.Form):
    owner = forms.ModelChoiceField(
        queryset=User.objects.filter(role=Role.CLIENT),
        required=False,  # Не обов'язкове
        # label="Виберіть користувача",  # Текст для поля
        empty_label="Виберіть замовника",  # Текст для пустого значення
        to_field_name='id',  # Вказуємо поле, яке будемо використовувати для значення
    )

    # Визначаємо, як будуть відображатися елементи списку
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.username})"


class UploadSinglePhotoForm(UploadOwner):
    title = forms.CharField(max_length=200, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    image = forms.ImageField(label='Upload Image', validators=[file_validation])
    


class UploadPhotosFromDirectoryForm(UploadOwner):
    directory_path = forms.CharField(label='Directory Path', max_length=255)
