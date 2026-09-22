from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class CustomLoginViewTests(TestCase):
    """Unit tests for user login and logout."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='loginuser', password='CorrectPassword123!')
        self.login_url = reverse('pages:login')
        self.logout_url = reverse('pages:logout')
        self.home_url = reverse('pages:home')

    def test_login_page_get(self):
        """GET request renders the login page."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_valid_credentials(self):
        """POST with valid credentials authenticates user and redirects."""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'CorrectPassword123!',
        })
        self.assertRedirects(response, self.home_url)
        # Check that session is authenticated
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_invalid_password(self):
        """POST with wrong password fails and keeps user unauthenticated."""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_nonexistent_user(self):
        """POST with non-existent username fails."""
        response = self.client.post(self.login_url, {
            'username': 'ghostuser',
            'password': 'SomePassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout(self):
        """Logging out terminates the session and redirects to home."""
        self.client.login(username='loginuser', password='CorrectPassword123!')
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.home_url)
        self.assertNotIn('_auth_user_id', self.client.session)

