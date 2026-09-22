from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesViewTests(TestCase):
    """Unit tests for general static pages (Home, About, Contact)."""

    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        """Home page loads successfully."""
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_about_view(self):
        """About page loads successfully."""
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_contact_view(self):
        """Contact page loads successfully."""
        response = self.client.get(reverse('pages:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

