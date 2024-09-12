from django.contrib import admin
from .models import Portfolio, Review

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_time')
    search_fields = ('title',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user','title', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
