from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # URL для списку блогів
    path('', views.BlogListView.as_view(), name='blog_list'),
    
    # URL для детальної сторінки блогу, де <slug> — це унікальний ідентифікатор блогу
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),

    # URL для перегляду детальної інформації про конкретний пост у блозі
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),

    # URL для створення нового поста
    path('<slug:slug>/post/new/', views.PostCreateView.as_view(), name='post_create'),

    # URL для редагування поста
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),

    # URL для видалення поста
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
