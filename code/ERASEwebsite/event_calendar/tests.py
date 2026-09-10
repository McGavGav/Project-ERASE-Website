from datetime import date, datetime, time
from unittest.mock import patch
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from .models import Event, RSVP
from .forms import EventForm
from .calendar_maker import (
    EventCalendar,
    resolve_month_year,
    get_navigation_dates,
    get_calendar_html,
    get_calendar_data,
)


class ResolveMonthYearTests(TestCase):
    """Boundary value and exception path tests for resolve_month_year."""

    def test_valid_integer_inputs(self):
        """Test with valid integer year and month."""
        self.assertEqual(resolve_month_year(2026, 5), (2026, 5))

    def test_valid_string_inputs(self):
        """Test with valid string numbers."""
        self.assertEqual(resolve_month_year("2025", "8"), (2025, 8))

    def test_none_inputs_defaults_to_current(self):
        """Test default fallback when year or month is None."""
        now = datetime.now()
        self.assertEqual(resolve_month_year(None, None), (now.year, now.month))
        self.assertEqual(resolve_month_year(2026, None), (2026, now.month))
        self.assertEqual(resolve_month_year(None, 7), (now.year, 7))

    # --- Boundary Value Testing for Month (1 <= month <= 12) ---

    def test_month_lower_boundary_valid(self):
        """Test lower valid boundary (month = 1, January)."""
        self.assertEqual(resolve_month_year(2026, 1), (2026, 1))

    def test_month_upper_boundary_valid(self):
        """Test upper valid boundary (month = 12, December)."""
        self.assertEqual(resolve_month_year(2026, 12), (2026, 12))

    def test_month_lower_boundary_invalid_zero(self):
        """Boundary test: month = 0 should fall back to current date."""
        now = datetime.now()
        self.assertEqual(resolve_month_year(2026, 0), (now.year, now.month))

    def test_month_upper_boundary_invalid_thirteen(self):
        """Boundary test: month = 13 should fall back to current date."""
        now = datetime.now()
        self.assertEqual(resolve_month_year(2026, 13), (now.year, now.month))

    # --- Exception Path Testing (ValueError and TypeError) ---

    def test_exception_path_value_error_string_year(self):
        """Exercise ValueError exception path when year string cannot be parsed as int."""
        now = datetime.now()
        self.assertEqual(resolve_month_year("invalid_year", 5), (now.year, now.month))

    def test_exception_path_value_error_string_month(self):
        """Exercise ValueError exception path when month string cannot be parsed as int."""
        now = datetime.now()
        self.assertEqual(resolve_month_year(2026, "invalid_month"), (now.year, now.month))

    def test_exception_path_type_error_unsupported_types(self):
        """Exercise TypeError exception path when passing non-string/non-int objects."""
        now = datetime.now()
        self.assertEqual(resolve_month_year([], {}), (now.year, now.month))
        self.assertEqual(resolve_month_year(object(), object()), (now.year, now.month))
        self.assertEqual(resolve_month_year([2026], 5), (now.year, now.month))


class GetNavigationDatesTests(TestCase):
    """Boundary value tests for get_navigation_dates."""

    def test_january_boundary(self):
        """Boundary test for January (month = 1): prev month should be December of previous year."""
        nav = get_navigation_dates(2026, 1)
        self.assertEqual(nav['display_date'], date(2026, 1, 1))
        self.assertEqual(nav['prev_month'], 12)
        self.assertEqual(nav['prev_year'], 2025)
        self.assertEqual(nav['next_month'], 2)
        self.assertEqual(nav['next_year'], 2026)

    def test_december_boundary(self):
        """Boundary test for December (month = 12): next month should be January of next year."""
        nav = get_navigation_dates(2026, 12)
        self.assertEqual(nav['display_date'], date(2026, 12, 1))
        self.assertEqual(nav['prev_month'], 11)
        self.assertEqual(nav['prev_year'], 2026)
        self.assertEqual(nav['next_month'], 1)
        self.assertEqual(nav['next_year'], 2027)

    def test_february_boundary(self):
        """Test February (month = 2) navigation."""
        nav = get_navigation_dates(2026, 2)
        self.assertEqual(nav['display_date'], date(2026, 2, 1))
        self.assertEqual(nav['prev_month'], 1)
        self.assertEqual(nav['prev_year'], 2026)
        self.assertEqual(nav['next_month'], 3)
        self.assertEqual(nav['next_year'], 2026)

    def test_november_boundary(self):
        """Test November (month = 11) navigation."""
        nav = get_navigation_dates(2026, 11)
        self.assertEqual(nav['display_date'], date(2026, 11, 1))
        self.assertEqual(nav['prev_month'], 10)
        self.assertEqual(nav['prev_year'], 2026)
        self.assertEqual(nav['next_month'], 12)
        self.assertEqual(nav['next_year'], 2026)

    def test_mid_year_month(self):
        """Test mid-year month (June, month = 6)."""
        nav = get_navigation_dates(2026, 6)
        self.assertEqual(nav['display_date'], date(2026, 6, 1))
        self.assertEqual(nav['prev_month'], 5)
        self.assertEqual(nav['prev_year'], 2026)
        self.assertEqual(nav['next_month'], 7)
        self.assertEqual(nav['next_year'], 2026)


class EventCalendarMakerTests(TestCase):
    """Tests for EventCalendar class, get_calendar_html, and get_calendar_data."""

    def setUp(self):
        self.event_date = date(2026, 5, 15)
        self.event = Event.objects.create(
            title="Science Workshop",
            date=self.event_date,
            time=time(14, 30),
            description="Hands-on science experiments",
            hasRSVP=True,
        )

    def test_event_calendar_formatday_zero(self):
        """Day 0 (empty placeholder outside month) returns other-month cell."""
        cal = EventCalendar()
        self.assertEqual(cal.formatday(0, 0), '<td class="other-month"></td>')

    def test_event_calendar_formatday_with_event(self):
        """Formatting a day with events renders the event pill."""
        events_dict = {self.event_date: [self.event]}
        cal = EventCalendar(events=events_dict)
        cal.year = 2026
        cal.month = 5

        day_html = cal.formatday(15, 4)
        self.assertIn('Science Workshop', day_html)
        self.assertIn('2:30 PM', day_html)
        self.assertIn('event-pill', day_html)
        self.assertIn('data-has-rsvp="true"', day_html)

    def test_event_calendar_formatday_today(self):
        """Formatting today's date applies the 'today' class."""
        today = datetime.now().date()
        cal = EventCalendar()
        cal.year = today.year
        cal.month = today.month

        day_html = cal.formatday(today.day, 0)
        self.assertIn('class="today"', day_html)
        self.assertIn('day-number-highlight', day_html)

    def test_event_calendar_formatweek(self):
        """Test formatting a calendar week row."""
        cal = EventCalendar()
        cal.year = 2026
        cal.month = 5
        week_data = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6)]
        week_html = cal.formatweek(week_data)
        self.assertTrue(week_html.startswith('<tr>'))
        self.assertTrue(week_html.endswith('</tr>'))

    def test_get_calendar_html(self):
        """Test get_calendar_html generates table markup."""
        events_dict = {self.event_date: [self.event]}
        html = get_calendar_html(2026, 5, events=events_dict)
        self.assertIn('<table', html)
        self.assertIn('Science Workshop', html)

    def test_get_calendar_data(self):
        """Test get_calendar_data returns complete dictionary context."""
        events_dict = {self.event_date: [self.event]}
        data = get_calendar_data("2026", "5", events=events_dict)

        self.assertEqual(data['current_year'], 2026)
        self.assertEqual(data['current_month'], 5)
        self.assertEqual(data['prev_month'], 4)
        self.assertEqual(data['prev_year'], 2026)
        self.assertEqual(data['next_month'], 6)
        self.assertEqual(data['next_year'], 2026)
        self.assertEqual(data['display_date'], date(2026, 5, 1))
        self.assertIn('Science Workshop', data['calendar_html'])


class EventModelsAndFormsTests(TestCase):
    """Tests for Event/RSVP models and EventForm."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.event = Event.objects.create(
            title="Community Meeting",
            date=date(2026, 6, 10),
            time=time(10, 0),
            description="Discussing community initiatives",
            hasRSVP=True,
        )

    def test_event_str(self):
        """Test string representation of Event model."""
        expected = "Community Meeting: 2026-06-10 at 10:00:00"
        self.assertEqual(str(self.event), expected)

    def test_rsvp_str(self):
        """Test string representation of RSVP model."""
        rsvp = RSVP.objects.create(event=self.event, user=self.user)
        expected = "testuser is RSVPed for Community Meeting"
        self.assertEqual(str(rsvp), expected)

    def test_event_form_valid(self):
        """Test valid EventForm submission."""
        form_data = {
            'title': 'New Event',
            'date': '2026-07-20',
            'time': '15:00',
            'description': 'Details here',
            'hasRSVP': True,
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())


class EventCalendarViewsTests(TestCase):
    """Tests for Calendar views and RSVP interactions."""

    def setUp(self):
        self.client = Client()
        self.normal_user = User.objects.create_user(username="normal", password="password123")
        self.staff_user = User.objects.create_user(username="staff", password="password123", is_staff=True)
        self.event = Event.objects.create(
            title="Robotics Intro",
            date=date(2026, 8, 15),
            time=time(13, 0),
            description="Robotics workshop",
            hasRSVP=True,
        )

    def test_calendar_view_get(self):
        """Test CalendarView GET request."""
        response = self.client.get(reverse('pages:calendar'), {'year': '2026', 'month': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Robotics Intro")
        self.assertEqual(response.context['current_year'], 2026)
        self.assertEqual(response.context['current_month'], 8)

    def test_add_event_view_staff_required(self):
        """Test that normal users cannot add events (PermissionDenied)."""
        self.client.login(username="normal", password="password123")
        response = self.client.post(reverse('pages:add_event'), {
            'title': 'Unauthorized Event',
            'date': '2026-08-20',
            'time': '10:00',
        })
        self.assertEqual(response.status_code, 403)

    def test_add_event_view_success_by_staff(self):
        """Test successful event creation by staff user."""
        self.client.login(username="staff", password="password123")
        response = self.client.post(reverse('pages:add_event'), {
            'title': 'Staff Added Event',
            'date': '2026-08-25',
            'time': '14:00',
            'description': 'Created by staff',
            'hasRSVP': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title='Staff Added Event').exists())

    def test_rsvp_toggle(self):
        """Test RSVP toggling (create then delete on second POST)."""
        self.client.login(username="normal", password="password123")
        rsvp_url = reverse('pages:rsvp_event', kwargs={'event_id': self.event.id})

        # First POST creates RSVP
        response = self.client.post(rsvp_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RSVP.objects.filter(event=self.event, user=self.normal_user).exists())

        # Second POST deletes RSVP
        response = self.client.post(rsvp_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RSVP.objects.filter(event=self.event, user=self.normal_user).exists())

    def test_rsvp_listing_and_detail_views(self):
        """Test RSVP listing and detail views for staff."""
        RSVP.objects.create(event=self.event, user=self.normal_user)
        self.client.login(username="staff", password="password123")

        # Listing view
        listing_res = self.client.get(reverse('pages:rsvp_listing'))
        self.assertEqual(listing_res.status_code, 200)
        self.assertContains(listing_res, "Robotics Intro")

        # Detail view
        detail_url = reverse('pages:rsvp_detail', kwargs={'event_id': self.event.id})
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "normal")
