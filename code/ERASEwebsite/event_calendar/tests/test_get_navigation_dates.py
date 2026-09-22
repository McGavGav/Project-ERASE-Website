from datetime import date
from django.test import TestCase
from event_calendar.calendar_maker import get_navigation_dates


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

