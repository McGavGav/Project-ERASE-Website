from django.contrib import admin
from .models import Workshop

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'date', 'latitude', 'longitude', 'created_by')
    list_filter = ('date', 'city', 'created_by')
    search_fields = ('title', 'description', 'city')
