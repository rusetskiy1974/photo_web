import zipfile
from io import BytesIO
from django.http import HttpResponse
import requests

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
