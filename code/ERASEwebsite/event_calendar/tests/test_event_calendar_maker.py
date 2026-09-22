from datetime import date, datetime, time
from django.test import TestCase
from event_calendar.models import Event
from event_calendar.calendar_maker import (
    EventCalendar,
    get_calendar_html,
    get_calendar_data,
)


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

