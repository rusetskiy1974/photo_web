from django.urls import path

from main import views

app_name ='main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('typography/', views.typography, name='typography'),
    path('contact/', views.contact, name='contact_me'),
    ]