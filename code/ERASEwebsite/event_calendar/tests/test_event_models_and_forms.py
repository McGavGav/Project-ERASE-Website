from datetime import date, time
from django.test import TestCase
from django.contrib.auth.models import User
from event_calendar.models import Event, RSVP
from event_calendar.forms import EventForm


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

