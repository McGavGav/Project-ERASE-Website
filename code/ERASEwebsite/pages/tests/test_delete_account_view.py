from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class DeleteAccountViewTests(TestCase):
    """Unit tests for user account self-deletion."""

    def setUp(self):
        self.client = Client()
        self.delete_url = reverse('pages:delete_account')
        self.account_url = reverse('pages:account')
        self.home_url = reverse('pages:home')
        self.normal_user = User.objects.create_user(username='deleteme', password='Password123!')
        self.superuser = User.objects.create_superuser(username='keepme', password='Password123!')

    def test_delete_account_requires_login(self):
        """Anonymous requests redirect to login."""
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)

    def test_delete_account_get_redirects_to_account(self):
        """GET request to delete_account redirects back to account view."""
        self.client.login(username='deleteme', password='Password123!')
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, self.account_url)

    def test_delete_account_post_by_normal_user_success(self):
        """POST by regular user deletes account from database and logs out."""
        self.client.login(username='deleteme', password='Password123!')
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.home_url)

        # Confirm user deleted
        self.assertFalse(User.objects.filter(username='deleteme').exists())
        # Confirm user logged out
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_delete_account_post_by_superuser_forbidden(self):
        """POST by superuser raises 403 PermissionDenied and does not delete superuser."""
        self.client.login(username='keepme', password='Password123!')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(username='keepme').exists())

