from django.test import TestCase
from students.models import Student


class StudentFilterTests(TestCase):
    """Unit tests for StudentQuerySet and StudentManager filtering and search capabilities."""

    def setUp(self):
        self.s1 = Student.objects.create(name="John Doe", gender="Male", school="Adams High")
        self.s2 = Student.objects.create(name="Jane Smith", gender="Female", school="Lincoln High")
        self.s3 = Student.objects.create(name="Bob Johnson", gender="Male", school="Lincoln High")
        self.s4 = Student.objects.create(name="Alice Williams", gender="Female", school="Adams High")

    def test_search_exact_match(self):
        """Search query matching exact name substring."""
        results = Student.objects.all().search("John")
        self.assertIn(self.s1, results)
        self.assertIn(self.s3, results)  # "Bob Johnson"
        self.assertNotIn(self.s2, results)
        self.assertNotIn(self.s4, results)

    def test_search_case_insensitive(self):
        """Search query should be case-insensitive."""
        results = Student.objects.all().search("jane")
        self.assertEqual(list(results), [self.s2])

    def test_search_none_or_empty_returns_all(self):
        """Empty or None query returns all records."""
        self.assertEqual(Student.objects.all().search("").count(), 4)
        self.assertEqual(Student.objects.all().search(None).count(), 4)

    def test_filter_gender_male(self):
        """Filter gender by Male."""
        results = Student.objects.all().filter_gender("Male")
        self.assertEqual(results.count(), 2)
        self.assertIn(self.s1, results)
        self.assertIn(self.s3, results)

    def test_filter_gender_female(self):
        """Filter gender by Female."""
        results = Student.objects.all().filter_gender("Female")
        self.assertEqual(results.count(), 2)
        self.assertIn(self.s2, results)
        self.assertIn(self.s4, results)

    def test_filter_gender_empty_returns_all(self):
        """Empty or None gender parameter returns all records."""
        self.assertEqual(Student.objects.all().filter_gender("").count(), 4)
        self.assertEqual(Student.objects.all().filter_gender(None).count(), 4)

    def test_filter_school_case_insensitive(self):
        """Filter school by case-insensitive partial substring."""
        results = Student.objects.all().filter_school("lincoln")
        self.assertEqual(results.count(), 2)
        self.assertIn(self.s2, results)
        self.assertIn(self.s3, results)

    def test_filter_school_empty_returns_all(self):
        """Empty or None school parameter returns all records."""
        self.assertEqual(Student.objects.all().filter_school("").count(), 4)
        self.assertEqual(Student.objects.all().filter_school(None).count(), 4)

    def test_apply_filters_combined(self):
        """Combining search, gender, and school filters narrows down results correctly."""
        # Male students at Lincoln High
        results = Student.objects.apply_filters(gender="Male", school="Lincoln")
        self.assertEqual(list(results), [self.s3])

        # Female students with 'Ali' in name
        results = Student.objects.apply_filters(search="Ali", gender="Female")
        self.assertEqual(list(results), [self.s4])

        # Female students at Adams High named Alice
        results = Student.objects.apply_filters(search="Alice", gender="Female", school="Adams")
        self.assertEqual(list(results), [self.s4])

    def test_apply_filters_no_matches(self):
        """Filters with no matching records return an empty QuerySet."""
        results = Student.objects.apply_filters(search="Nonexistent", gender="Male", school="Adams")
        self.assertEqual(results.count(), 0)
