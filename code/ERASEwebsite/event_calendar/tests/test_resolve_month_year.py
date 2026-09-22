from datetime import datetime
from django.test import TestCase
from event_calendar.calendar_maker import resolve_month_year


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

