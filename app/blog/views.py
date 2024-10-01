from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from .models import Blog, Post

# 1. Список всіх блогів
class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'  # Вкажіть шаблон
    context_object_name = 'blogs'  # Ім'я для використання в шаблоні

# 2. Детальна сторінка конкретного блогу
class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = Blog.objects.get(slug=self.kwargs['slug'])  # Додаємо об'єкт блогу з слагом
        return context

# 3. Детальна сторінка конкретного поста
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'  # Вкажіть шаблон
    context_object_name = 'post'  # Ім'я для використання в шаблоні

# 4. Створення нового поста
class PostCreateView(CreateView):
    model = Post
    template_name = 'blog/create_post.html'
    fields = ['title', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:blog_detail', kwargs={'slug': self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = get_object_or_404(Blog, slug=self.kwargs['slug'])  # Передаємо об'єкт блогу в контекст
        return context
    

# 5. Редагування поста
class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/post_form.html'  # Вкажіть шаблон
    fields = ['title', 'content', 'image', 'blog']  # Поля для редагування
    success_url = reverse_lazy('blog:blog_list')  # Переадресація після редагування

# 6. Видалення поста
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'  # Вкажіть шаблон для підтвердження видалення
    success_url = reverse_lazy('blog:blog_list')  # Переадресація після видалення





