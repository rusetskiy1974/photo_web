from django.forms import ModelForm

import cloudinary
import hashlib
# Next two lines are only used for generating the upload preset sample name
from cloudinary.compat import to_bytes
from cloudinary.forms import CloudinaryJsFileField, CloudinaryUnsignedJsFileField
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


class UploadSinglePhotoForm(forms.Form):
    title = forms.CharField(max_length=200, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    image = forms.ImageField(label='Upload Image', validators=[file_validation])