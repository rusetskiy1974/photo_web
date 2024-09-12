from django.urls import path

from services import views

app_name = 'services'

urlpatterns = [
    path('search/', views.CatalogView.as_view(), name='search'),
    path('<slug:category_slug>/', views.CatalogView.as_view(), name='index'),
    path('service/<slug:service_slug>/', views.ServiceView.as_view(), name='service'),
]