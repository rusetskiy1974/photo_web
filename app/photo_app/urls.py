from django.urls import path

from photo_app import views

app_name = 'photo_app'

urlpatterns = [
    path('public_list/', views.public_list, name='public_list'),
    # URL for uploading an image
    path('upload/', views.upload, name='upload'),
    # The direct upload functionality reports to this URL when an image is uploaded.
    path('upload/complete', views.direct_upload_complete, name='direct_upload_complete'),
    
]
    