from django.contrib import admin
from .models import Event, RSVP


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'hasRSVP')
    list_filter = ('date', 'hasRSVP')
    search_fields = ('title', 'description')


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'reserved_at')
    list_filter = ('event', 'reserved_at')
    search_fields = ('user__username', 'event__title')

