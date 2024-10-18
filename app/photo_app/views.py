import json
import zipfile
import io
from django.contrib import messages
from django.urls import reverse
import six
import requests
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.db.models import Avg, FloatField, F, OuterRef, Subquery, Value
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from cloudinary import api  # Only required for creating upload presets on the fly
from cloudinary.forms import cl_init_js_callbacks

from .forms import PhotoForm, PhotoDirectForm, PhotoUnsignedDirectForm
from .models import Photo, Rating
from .utils.utils import TRANSFORMS, mark_photos, cloudinary_transform


def filter_nones(d):
    return dict((k, v) for k, v in six.iteritems(d) if v is not None)



@login_required
def public_list(request):
    # Отримуємо всі публічні фото та обчислюємо середній рейтинг (null для відсутніх рейтингів замінюємо на 0)
    public_photos = Photo.objects.filter(is_public=True).annotate(
        avg_rating=Coalesce(Avg('ratings__value'), 0.0, output_field=FloatField())  # Вказуємо, що це FloatField
    ).order_by(F('avg_rating').desc(nulls_last=True))  # Сортуємо за рейтингом, фото без рейтингу йдуть останні

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = mark_photos(public_photos, request.user)

    # Пагінація
    paginator = Paginator(photos_with_text, 8)  # 8 фото на сторінку
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Clients public photos',
        'page_obj': page_obj,  # Замість всіх фото передаємо тільки поточну сторінку
    }

    return render(request, 'photo_app/public_list.html', context)


@login_required
def set_ratings(request):
    user = request.user
    # Отримуємо всі публічні фото (is_public=True)
    user_ratings = Rating.objects.filter(
    photo=OuterRef('pk'),  # Порівнюємо з полем "photo"
    user=user  # Рейтинг для поточного користувача
).values('value')[:1]
    
    public_photos = Photo.objects.filter(is_public=True).annotate(
    user_rating=Coalesce(
        Subquery(user_ratings),  # Рейтинг від користувача, якщо є
        Value(0)  # Якщо немає, підставляємо 0
    )
).order_by('-user_rating')
    
    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = mark_photos(public_photos, request.user)

    # Пагінація
    paginator = Paginator(photos_with_text, 8)  # 8 фото на сторінку
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Set Ratings for photos',
        'page_obj': page_obj,  # Замість всіх фото передаємо тільки поточну сторінку
        
    }

    return render(request, 'photo_app/set_ratings.html', context)


@login_required
@require_POST  # Цей декоратор сам гарантує, що метод POST
def rate_photo(request, photo_id):
    """
    Обробляє POST-запит для оцінки фото.
    """
    photo = get_object_or_404(Photo, id=photo_id)  # Отримуємо фото за id або повертаємо 404

    try:
        data = json.loads(request.body)  # Парсимо JSON-дані
        rating_value = int(data.get('rating'))  # Отримуємо значення рейтингу з JSON

        # Перевіряємо, чи існує вже оцінка від цього користувача для цього фото
        rating, created = Rating.objects.get_or_create(
            photo=photo, 
            user=request.user,
            defaults={'value': rating_value}
        )

        # Якщо оцінка вже існує, оновлюємо її
        if not created:
            rating.value = rating_value
            rating.save()

        return JsonResponse({
            'success': True,
            'user_rating': rating.value,  # Повертаємо рейтинг, який надав користувач
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid rating value'}, status=400)



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


@login_required
def my_photos(request):
    my_photos = Photo.objects.filter(owner=request.user.id)

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = mark_photos(my_photos, request.user)

    paginator = Paginator(photos_with_text, 8)  # 8 фото на сторінку
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Отримуємо всі ID фотографій
    all_photo_ids = my_photos.values_list('id', flat=True)

    context = {
        'title': 'My photos',
        'page_obj': page_obj,   # Пагінація для відображення фото на поточній сторінці
        'all_photo_ids': all_photo_ids,  # Передаємо всі ID фото
    }

    return render(request, 'photo_app/my_photos.html', context)

@login_required
def handle_my_photos(request):
    my_photos = Photo.objects.filter(owner=request.user.id)

    # Створюємо URL з трансформацією, яка накладає текст "Фотостудія RMS"
    photos_with_text = mark_photos(my_photos, request.user)

    paginator = Paginator(photos_with_text, 8)  # 8 фото на сторінку
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Отримуємо всі ID фотографій
    all_photo_ids = my_photos.values_list('id', flat=True)

    context = {
        'title': 'Handle photos',
        'page_obj': page_obj,   # Пагінація для відображення фото на поточній сторінці
        'all_photo_ids': all_photo_ids,  # Передаємо всі ID фото
    }

    return render(request, 'photo_app/handle_my_photos.html', context)


@login_required
def handle_photos(request):
    # Отримуємо поточну сторінку з GET або POST запитів
    obj_page = request.GET.get('page', request.POST.get('obj_page', '1'))  # Отримуємо поточну сторінку або 1 за замовчуванням

    if request.method == 'POST':
        # Отримуємо список вибраних фото з форми
        selected_photo_ids = request.POST.get('selected_photo_ids', '')
        
        if selected_photo_ids:
            # Розділяємо рядок з ID на список чисел
            selected_photo_ids_list = selected_photo_ids.split(',')
            try:
                # Перетворюємо кожен елемент у список цілих чисел
                # selected_photo_ids = [int(photo_id) for photo_id in selected_photo_ids if photo_id]
                
                # Знаходимо відповідні фото
                selected_photos = Photo.objects.filter(id__in=selected_photo_ids_list)
                
                # Обробка дій в залежності від кнопки
                action = request.POST.get('action')
                
                if action == 'publish':
                    selected_photos.update(is_public=True)
                    messages.success(request, f"{selected_photos.count()} photos were made public.")

                elif action == 'private':
                    selected_photos.update(is_public=False)
                    messages.success(request, f"{selected_photos.count()} photos were made private.")

                elif action == 'cloudinary_transformation':  
                    # selected_photo_ids_list = selected_photo_ids.split(',')
                    # selected_photos = Photo.objects.filter(id__in=selected_photo_ids_list)
                    type_transformation = list(TRANSFORMS.keys())
                    transformation_type = 'mark_photos'
                    paginator = Paginator(selected_photos, 8)
                    page_number = request.GET.get('page', '1')
                    page_obj = paginator.get_page(page_number)

                    context = {
                        # 'title': 'Cloudinary Transformation',
                        # 'page_obj': page_obj,
                        'selected_photo_ids': selected_photo_ids,
                        # 'type_transformation': type_transformation,
                        'transformation_type': transformation_type,
                        
                    }
                    # return render(request, 'photo_app/transforms.html', context)
                    # return redirect(f"{reverse('photo_app:transforms')}?transformation_type={transformation_type}&selected_photo_ids={selected_photo_ids}")
                    return render(request, 'photo_app/transforms_redirect.html', context)
                
                elif action == 'download':
                    # Логіка завантаження фото, якщо потрібно
                    messages.success(request, f"{selected_photos.count()} photos were prepared for download.")
                
                # Повертаємо на ту саму сторінку пагінації після дії
                return redirect(f"{reverse('photo_app:handle_my_photos')}?page={obj_page}")
            
            except ValueError:
                messages.error(request, "Invalid photo IDs. Please try again.")
        else:
            messages.warning(request, "No photos were selected.")
    
    # Якщо метод GET або POST без валідних даних, перенаправляємо на сторінку
    return redirect(f"{reverse('photo_app:handle_my_photos')}?page={obj_page}")

    
@login_required
def transforms(request):
    # Отримуємо параметри сторінки та типу трансформації
    obj_page = request.GET.get('obj_page', request.POST.get('page', '1'))
    selected_photo_ids = request.POST.get('selected_photo_ids', '')
    # transformation_type = request.GET.get('transformation_type', request.session.get('transformation_type', None))

    # Перевіряємо наявність `transformation_type`, щоб уникнути помилки
    # if not transformation_type:
    #     messages.error(request, "Transformation type is missing.")
    #     return redirect(f"{reverse('photo_app:handle_my_photos')}")  # Якщо тип трансформації не знайдено

    if request.method == 'POST':
        
        selected_photo_ids_list = selected_photo_ids.split(',')
        transformation_type = request.POST.get('transformation_type')

        if selected_photo_ids:
            try:
                # Отримуємо фото по ID
                selected_photos = Photo.objects.filter(id__in=selected_photo_ids_list)
                
                # if not selected_photos.exists():
                #     messages.error(request, "No photos selected.")
                #     return redirect(f"{reverse('photo_app:handle_my_photos')}?page={obj_page}")
                
                # Застосовуємо трансформацію
                photos_for_transforms = cloudinary_transform(selected_photos, transformation_type)

                # Зберігаємо ID трансформованих фото в сесії для подальшого використання
                request.session['selected_photo_ids'] = selected_photo_ids
                request.session['transformation_type'] = transformation_type

                # Пагінація
                paginator = Paginator(photos_for_transforms, 8)  # 8 фото на сторінку
                page_obj = paginator.get_page(obj_page)

                context = {
                    'title': f'Cloudinary Transformation: {transformation_type}',
                    'page_obj': page_obj,
                    'type_transformation': list(TRANSFORMS.keys()),  
                    'obj_page': obj_page,
                    'selected_photo_ids': selected_photo_ids,
                    'transformation_type': transformation_type,
                }

                return render(request, 'photo_app/transforms.html', context)

            except ValueError:
                messages.error(request, "Invalid photo IDs.")
                return redirect(f"{reverse('photo_app:handle_my_photos')}?page={obj_page}")

        else:
            messages.warning(request, "No photos selected.")
            return redirect(f"{reverse('photo_app:handle_my_photos')}?page={obj_page}")

    elif request.method == 'GET':
        # Відновлюємо фото з трансформаціями з сесії
        # selected_photo_ids = request.GET.get('selected_photo_ids')
        selected_photo_ids = request.session.get('selected_photo_ids', [])
        transformation_type = request.GET.get('transformation_type')
        selected_photo_ids_list = selected_photo_ids.split(',')
        
        selected_photos = Photo.objects.filter(id__in=selected_photo_ids_list)

        
        # Застосовуємо трансформацію
        photos_with_transforms = cloudinary_transform(selected_photos, transformation_type)
        
        paginator = Paginator(photos_with_transforms, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        

        context = {
            'title': f'Cloudinary Transformation: {transformation_type}',
            'page_obj': page_obj,
            'type_transformation': list(TRANSFORMS.keys()),
            'obj_page': obj_page,
            'selected_photo_ids': selected_photo_ids,
            'transformation_type': transformation_type,
        }

        return render(request, 'photo_app/transforms.html', context)

    return redirect(f"{reverse('photo_app:handle_my_photos')}?page={obj_page}")
