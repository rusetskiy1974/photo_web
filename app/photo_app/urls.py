from django.urls import path

from photo_app import views

app_name = 'photo_app'

urlpatterns = [
     # URL for listing all images:
    path('', views.list, name='list'),
    path('list/', views.list, name='list'),
    # URL for uploading an image
    path('upload/', views.upload, name='upload'),
    # The direct upload functionality reports to this URL when an image is uploaded.
    path('upload/complete', views.direct_upload_complete, name='direct_upload_complete'),
]
    