from django.urls import path

from . import views

app_name ='main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('typography/', views.typography, name='typography'),
    path('contact/', views.contact, name='contact_me'),
    path('portfolio/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('rate-photo/<int:photo_id>/', views.rate_photo, name='rate_photo'),
    ]
