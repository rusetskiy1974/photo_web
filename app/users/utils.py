import zipfile
from io import BytesIO
from django.http import HttpResponse
import requests
from cloudinary import CloudinaryImage

from photo_app.models import Photo, Rating

def download_photos_as_zip(photos):
    # Створюємо архів у пам'яті
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for photo in photos:
            # Завантажуємо зображення за URL-адресою
            response = requests.get(photo.image_url)
            if response.status_code == 200:
                # Додаємо файл до архіву
                zip_file.writestr(f"{photo.title}.jpg", response.content)
    
    zip_buffer.seek(0)

    # Повертаємо архів як відповідь
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="photos.zip"'
    return response

def mark_photos(photos: list[Photo], user) -> list[Photo]:
    photos_with_text = []
    for photo in photos:
        url_with_text = CloudinaryImage(photo.public_id).build_url(transformation=[
  {'width': 500, 'crop': "scale"},
  {'color': "#FFFFFF80", 'overlay': {'font_family': "Times", 'font_size': 90, 'font_weight': "bold", 'text': "Photo RMS"}},
  {'flags': "layer_apply", 'gravity': "center", 'y': 20}
  ])
        rating = Rating.objects.filter(photo=photo, user=user).first()
        photos_with_text.append({
            'photo': photo,
            'url_with_text': url_with_text,
            'rating': rating,
        })
    return photos_with_text    