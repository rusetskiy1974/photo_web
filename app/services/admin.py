from django.contrib import admin
from .models import Category, Service

@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(Service)
class ServicesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "duration", "price", "created_by"]
    search_fields = ["name", "description"]
    list_filter = ["duration", "category", "created_by"]
    readonly_fields = ["created_at"] 
    fields = [
        "name",
        "category",
        "slug",
        "description",
        "image",
        "price",
        "duration",
        "created_by",
        "created_at",
    ]
