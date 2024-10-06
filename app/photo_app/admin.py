import os
from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.template.response import TemplateResponse
from .models import Photo
from cloudinary import uploader
from .forms import UploadSinglePhotoForm, UploadPhotosFromDirectoryForm
from .utils.image_validator import validate_download_file_size


class PhotoAdmin(admin.ModelAdmin):
    # Додаємо кастомні дії
    @admin.action(description="Upload Single Photo")
    def upload_single_action(self, request, queryset):  # Потрібно додати параметр queryset
        self.message_user(request, "Redirecting to Upload Single Photo page.")
        return HttpResponseRedirect(reverse('admin:upload_single_photo'))

    @admin.action(description="Upload Photos from Directory")
    def upload_directory_action(self, request, queryset):  # Параметр queryset також тут
        self.message_user(request, "Redirecting to Upload Photos from Directory page.")
        return HttpResponseRedirect(reverse('admin:upload_photos_from_directory'))


    list_display = ('title', 'create_time', 'public_id')
    search_fields = ('title',)
    list_filter = ('create_time',)

    
    add_form_template = "admin/photo_add_form.html"
    change_list_template = "admin/photo_change_list.html" 


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-single/', self.admin_site.admin_view(self.upload_single), name='upload_single_photo'),
            path('upload-directory/', self.admin_site.admin_view(self.upload_directory), name='upload_photos_from_directory'),
        ]
        return custom_urls + urls

    def upload_single(self, request):
        if request.method == 'POST':
            try:
                form = UploadSinglePhotoForm(request.POST, request.FILES)
                if form.is_valid():
                    # Створюємо новий екземпляр моделі Photo
                    photo = Photo(
                        title=form.cleaned_data['title'],
                        description=form.cleaned_data['description'],
                        owner=form.cleaned_data['owner'],
                    )
                    
                    # Використовуємо метод upload_image для завантаження фото на Cloudinary
                    image_file = form.cleaned_data['image']
                    photo.upload_image(image_file)
                    
                    # Зберігаємо фото в базі даних
                    photo.save()
                    
                    self.message_user(request, "Photo uploaded successfully.")
                    return HttpResponseRedirect(request.path_info)
            except Exception as e:
                self.message_user(request, f"Error uploading photo: {str(e)}", level='error')
        else:
            form = UploadSinglePhotoForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/upload_single_photo.html', context)


    def upload_directory(self, request):
        if request.method == 'POST':
            form = UploadPhotosFromDirectoryForm(request.POST)
            if form.is_valid():
                directory_path = form.cleaned_data['directory_path']
                owner_id = form.cleaned_data['owner']
                
                if os.path.isdir(directory_path):
                    count_photos = 0
                    for filename in os.listdir(directory_path):
                        try:
                            # Перевіряємо чи файл є зображенням
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                                file_path = os.path.join(directory_path, filename)
                                
                                # Валідуємо розмір файлу
                                validate_download_file_size(file_path)
                                
                                # Відкриваємо файл для читання у байтовому режимі
                                with open(file_path, 'rb') as f:
                                    # Створюємо новий екземпляр Photo
                                    file_name, _ = os.path.splitext(filename)
                                    photo = Photo(
                                        title=file_name,
                                        description=file_name,
                                        owner=owner_id,
                                    )
                                    
                                    # Використовуємо метод upload_image для завантаження фото
                                    photo.upload_image(f)
                                    count_photos+=1
                                                                        
                        except Exception as e:
                            self.message_user(request, f"Error processing file '{filename}': {str(e)}", level='error')
                            
                    # Повідомляємо про успішне завантаження
                    self.message_user(request, f"{count_photos} photos uploaded successfully.")
                    return HttpResponseRedirect(request.path_info)
                else:
                    self.message_user(request, "Invalid directory path.", level='error')
        else:
            form = UploadPhotosFromDirectoryForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/upload_photos_from_directory.html', context)

    # При видаленні фотографії також видаляємо з Cloudinary
    def delete_model(self, request, obj):
        if obj.public_id:
            uploader.destroy(obj.public_id)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.public_id:
                uploader.destroy(obj.public_id)
        queryset.delete()

    
admin.site.register(Photo, PhotoAdmin)
