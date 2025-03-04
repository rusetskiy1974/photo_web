from django.contrib import admin

from .models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_time')
    search_fields = ('title',)

