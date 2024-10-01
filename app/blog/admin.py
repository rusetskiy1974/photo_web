from django.contrib import admin
from .models import Post, Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', "description", 'created_at', 'created_by')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('blog','title', 'author', 'published_at' )
    list_filter = ('published_at', 'author', 'blog')
    search_fields = ('title', 'content')