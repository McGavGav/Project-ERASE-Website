from django.urls import path
from .views import (
    CalendarView,
    AddEventView,
    RSVPEventView,
    RSVPListingView,
    RSVPDetailView,
)

app_name = 'event_calendar'

urlpatterns = [
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('calendar/add-event/', AddEventView.as_view(), name='add_event'),
    path('calendar/rsvp/<int:event_id>/', RSVPEventView.as_view(), name='rsvp_event'),
    path('rsvp-listing/', RSVPListingView.as_view(), name='rsvp_listing'),
    path('rsvp-listing/<int:event_id>/', RSVPDetailView.as_view(), name='rsvp_detail'),
]

