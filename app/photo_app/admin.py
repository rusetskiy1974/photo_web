import os
from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.template.response import TemplateResponse
from .models import Photo
from cloudinary import uploader
from .forms import UploadSinglePhotoForm
from .utils.image_validator import validate_download_file_size


class UploadPhotosFromDirectoryForm(forms.Form):
    directory_path = forms.CharField(label='Directory Path', max_length=255)




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
                    image_file = form.cleaned_data['image']
                    cloudinary_response = uploader.upload(image_file)
                    Photo.objects.create(
                        title=form.cleaned_data['title'],
                        description=form.cleaned_data['description'],
                        public_id=cloudinary_response['public_id'],
                    )
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
                if os.path.isdir(directory_path):
                    for filename in os.listdir(directory_path):
                        try:
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                                file_path = os.path.join(directory_path, filename)
                                validate_download_file_size(file_path)
                                with open(file_path, 'rb') as f:
                                    cloudinary_response = uploader.upload(f)
                                    file_name, _ = os.path.splitext(filename)
                                    Photo.objects.create(
                                        title=file_name,
                                        description=file_name,
                                        public_id=cloudinary_response['public_id']
                                    )
                        except Exception as e:
                            self.message_user(request, f"Error processing file '{filename}': {str(e)}", level='error')            
                    self.message_user(request, "Photos uploaded successfully.")
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
