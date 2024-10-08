from django.contrib import admin

from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user','title', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

