from django.urls import path

from . import views

app_name ='reviews'

urlpatterns = [
    path('', views.reviews_list, name='reviews_list'),  # Список рецензій
    path('create/', views.review_create, name='review_create'),  # Створення рецензії
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),  # Деталі рецензії
    path('<int:pk>/edit/', views.review_edit, name='review_edit'),  # Редагування рецензії
    path('<int:pk>/delete/', views.review_delete, name='review_delete'),  # Видалення рецензії
]