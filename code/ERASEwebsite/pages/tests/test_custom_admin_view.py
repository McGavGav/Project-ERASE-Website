from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class CustomAdminViewTests(TestCase):
    """Unit tests for custom admin dashboard metrics view."""

    def setUp(self):
        self.client = Client()
        self.admin_url = reverse('pages:custom_admin')
        self.superuser = User.objects.create_superuser(username='headadmin', password='Password123!')
        self.staff_user = User.objects.create_user(username='staffmember', password='Password123!', is_staff=True)
        self.regular_user = User.objects.create_user(username='simpleuser', password='Password123!')

    def test_custom_admin_requires_staff_or_superuser(self):
        """Regular users receive 403 PermissionDenied."""
        self.client.login(username='simpleuser', password='Password123!')
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 403)

    def test_custom_admin_accessible_by_staff_and_superuser(self):
        """Staff and superusers can view dashboard with correct user statistics."""
        self.client.login(username='staffmember', password='Password123!')
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin.html')
        self.assertEqual(response.context['total_users'], 3)
        self.assertEqual(response.context['staff_count'], 1)
        self.assertEqual(response.context['superuser_count'], 1)

