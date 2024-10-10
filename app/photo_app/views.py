import json
import zipfile
import io
from django.core.paginator import Paginator
import requests

import six
from cloudinary import api  # Only required for creating upload presets on the fly
from cloudinary.forms import cl_init_js_callbacks
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, render
from django.contrib.auth.decorators import login_required

from .forms import PhotoForm, PhotoDirectForm, PhotoUnsignedDirectForm
from .models import Photo
from users.utils import mark_photos


def filter_nones(d):
    return dict((k, v) for k, v in six.iteritems(d) if v is not None)



@login_required
def public_list(request):
    # Отримуємо всі публічні фото (is_public=True)
    public_photos = Photo.objects.filter(is_public=True)

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = mark_photos(public_photos)
    
    # Пагінація
    paginator = Paginator(photos_with_text, 8)  # 8 фото на сторінку
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Clients public photos',
        'page_obj': page_obj,  # Замість всіх фото передаємо тільки поточну сторінку
    }

    return render(request, 'photo_app/public_list.html', context)


def upload(request):
    unsigned = request.GET.get("unsigned") == "true"

    if (unsigned):
        # For the sake of simplicity of the sample site, we generate the preset on the fly.
        # It only needs to be created once, in advance.
        try:
            api.upload_preset(PhotoUnsignedDirectForm.upload_preset_name)
        except api.NotFound:
            api.create_upload_preset(name=PhotoUnsignedDirectForm.upload_preset_name, unsigned=True,
                                     folder="preset_folder")

    direct_form = PhotoUnsignedDirectForm() if unsigned else PhotoDirectForm()
    context = dict(
        # Form demonstrating backend upload
        backend_form=PhotoForm(),
        # Form demonstrating direct upload
        direct_form=direct_form,
        # Should the upload form be unsigned
        unsigned=unsigned,
    )
    # When using direct upload - the following call is necessary to update the
    # form's callback url
    cl_init_js_callbacks(context['direct_form'], request)

    if request.method == 'POST':
        # Only backend upload should be posting here
        form = PhotoForm(request.POST, request.FILES)
        context['posted'] = form.instance
        if form.is_valid():
            # Uploads image and creates a model instance for it
            form.save()
        else:
            context['posted'].errors = form.errors

    return render(request, 'photo_app/upload.html', context)


def direct_upload_complete(request):
    form = PhotoDirectForm(request.POST)
    if form.is_valid():
        # Create a model instance for uploaded image using the provided data
        form.save()
        ret = dict(photo_id=form.instance.id)
    else:
        ret = dict(errors=form.errors)

    return HttpResponse(json.dumps(ret), content_type='application/json')

def download_multiple_photos(request):
    # Передбачається, що ви отримуєте список ID фотографій з GET-запиту (або POST, залежно від вашої форми).
    photo_ids = request.GET.getlist('photo_ids')

    if not photo_ids:
        return HttpResponse("Не вибрано жодного фото.", status=400)

    # Отримуємо фотографії за переданими ID
    photos = get_list_or_404(Photo, id__in=photo_ids)

    # Створюємо об'єкт в пам'яті для запису архіву
    buffer = io.BytesIO()

    # Створюємо архів
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for photo in photos:
            # Завантажуємо кожне фото через URL
            response = requests.get(photo.image_url)
            if response.status_code == 200:
                # Створюємо ім'я файлу для архіву
                file_name = f"{photo.title or 'photo'}_{photo.pk}.jpg"
                # Записуємо зображення в архів
                zip_file.writestr(file_name, response.content)

    # Після створення архіву, переміщаємо курсор на початок файлу
    buffer.seek(0)

    # Створюємо відповідь з файлом архіву для завантаження
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="photos.zip"'

    return response

