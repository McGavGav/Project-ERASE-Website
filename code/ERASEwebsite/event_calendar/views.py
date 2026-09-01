from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count

from .models import Event, RSVP
from .forms import EventForm
from .calendar_maker import get_calendar_html


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin ensuring the user is staff or superuser."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('pages:login')
        raise PermissionDenied


class CalendarView(View):
    """Class-Based View for rendering the events calendar."""
    template_name = 'calendar.html'

    def get(self, request, *args, **kwargs):
        now = datetime.now()
        current_month = request.GET.get('month', now.month)
        current_year = request.GET.get('year', now.year)

        try:
            current_month = int(current_month)
            current_year = int(current_year)
        except (ValueError, TypeError):
            current_month = now.month
            current_year = now.year

        month_events = Event.objects.filter(date__year=current_year, date__month=current_month)
        events_by_date = {}
        for event in month_events:
            events_by_date.setdefault(event.date, []).append(event)

        calendar_html = get_calendar_html(current_year, current_month, events_by_date)

        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year

        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year

        event_form = EventForm()
        event_added = request.GET.get('event_added') == '1'

        rsvped_ids = set()
        if request.user.is_authenticated:
            rsvped_ids = set(
                RSVP.objects.filter(user=request.user, event__in=month_events)
                .values_list('event_id', flat=True)
            )

        context = {
            'calendar_html': calendar_html,
            'current_month': current_month,
            'current_year': current_year,
            'display_date': date(current_year, current_month, 1),
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'event_form': event_form,
            'event_added': event_added,
            'rsvped_ids': list(rsvped_ids),
        }

        return render(request, self.template_name, context)


class AddEventView(LoginRequiredMixin, StaffRequiredMixin, View):
    """Class-Based View for adding a calendar event."""
    def post(self, request, *args, **kwargs):
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            month = form.cleaned_data['date'].month
            year = form.cleaned_data['date'].year
            return redirect(f"{reverse('pages:calendar')}?month={month}&year={year}&event_added=1")
        return redirect('pages:calendar')

    def get(self, request, *args, **kwargs):
        return redirect('pages:calendar')


class RSVPEventView(LoginRequiredMixin, View):
    """Class-Based View for toggling RSVP on an event."""
    def post(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, pk=event_id)
        if not event.hasRSVP:
            raise PermissionDenied

        rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
        if not created:
            rsvp.delete()

        return redirect(f"{reverse('pages:calendar')}?month={event.date.month}&year={event.date.year}")

    def get(self, request, event_id, *args, **kwargs):
        return redirect('pages:calendar')


class RSVPListingView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Class-Based View for listing events that require RSVP."""
    template_name = 'rsvp_listing.html'
    context_object_name = 'events'

    def get_queryset(self):
        return (
            Event.objects.filter(hasRSVP=True)
            .order_by('date', 'time')
            .annotate(rsvp_count=Count('rsvps'))
        )


class RSVPDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Class-Based View for viewing attendees of an RSVP event."""
    template_name = 'rsvp_detail.html'
    model = Event
    pk_url_kwarg = 'event_id'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(hasRSVP=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rsvps'] = self.object.rsvps.select_related('user').order_by('reserved_at')
        return context

