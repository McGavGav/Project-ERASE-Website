from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class SignUpViewTests(TestCase):
    """Unit tests for user registration / signup."""

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('pages:signup')
        self.login_url = reverse('pages:login')

    def test_signup_page_get(self):
        """GET request loads the signup page with a blank UserCreationForm."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
        self.assertIn('form', response.context)

    def test_signup_successful_registration(self):
        """Valid registration creates a user, adds to 'normal users' group, and redirects to login."""
        post_data_django = {
            'username': 'newuser123',
            'password1': 'ComplexPassword!456',
            'password2': 'ComplexPassword!456',
        }
        response = self.client.post(self.signup_url, data=post_data_django)
        self.assertRedirects(response, self.login_url)

        # Verify user was created in database
        self.assertTrue(User.objects.filter(username='newuser123').exists())
        user = User.objects.get(username='newuser123')

        # Verify user is assigned to 'normal users' group
        self.assertTrue(user.groups.filter(name='normal users').exists())

    def test_signup_password_mismatch(self):
        """Registration with mismatched passwords fails and does not create user."""
        post_data = {
            'username': 'baduser',
            'password1': 'Password123!',
            'password2': 'DifferentPassword456!',
        }
        response = self.client.post(self.signup_url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='baduser').exists())
        self.assertTrue(response.context['form'].errors)

    def test_signup_duplicate_username(self):
        """Registration with an already existing username fails."""
        User.objects.create_user(username='existinguser', password='Password123!')
        post_data = {
            'username': 'existinguser',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        response = self.client.post(self.signup_url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

