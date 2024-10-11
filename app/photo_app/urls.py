from django.urls import path

from . import views

app_name = 'photo_app'

urlpatterns = [
    path('public_list/', views.public_list, name='public_list'),
    path('ratings/', views.set_ratings, name='ratings'),
    path('ratings/<int:photo_id>/rate/', views.rate_photo, name='rate_photo'),
    # URL for uploading an image
    # path('upload/', views.upload, name='upload'),
    # # The direct upload functionality reports to this URL when an image is uploaded.
    # path('upload/complete', views.direct_upload_complete, name='direct_upload_complete'),
    
]
    
