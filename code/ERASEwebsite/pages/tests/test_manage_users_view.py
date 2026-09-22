from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class ManageUsersViewTests(TestCase):
    """Unit tests for superuser manage-users view (grant/revoke staff permissions)."""

    def setUp(self):
        self.client = Client()
        self.manage_url = reverse('pages:manage_users')
        self.superuser = User.objects.create_superuser(username='boss', password='Password123!')
        self.target_user = User.objects.create_user(username='target', password='Password123!', is_staff=False)
        self.normal_user = User.objects.create_user(username='regular', password='Password123!')

    def test_manage_users_requires_superuser(self):
        """Non-superusers receive 403 PermissionDenied."""
        # Anonymous
        res_anon = self.client.get(self.manage_url)
        self.assertEqual(res_anon.status_code, 302)

        # Normal user
        self.client.login(username='regular', password='Password123!')
        res_normal = self.client.get(self.manage_url)
        self.assertEqual(res_normal.status_code, 403)

    def test_manage_users_get_by_superuser(self):
        """Superuser GET renders manage_users.html with user list excluding self."""
        self.client.login(username='boss', password='Password123!')
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_users.html')
        users = response.context['users']
        self.assertIn(self.target_user, users)
        self.assertNotIn(self.superuser, users)

    def test_manage_users_grant_staff(self):
        """Superuser can grant staff privileges to a normal user."""
        self.client.login(username='boss', password='Password123!')
        response = self.client.post(self.manage_url, {
            'user_id': self.target_user.pk,
            'action': 'grant',
        })
        self.assertRedirects(response, self.manage_url)

        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_staff)

    def test_manage_users_revoke_staff(self):
        """Superuser can revoke staff privileges from a staff user."""
        self.target_user.is_staff = True
        self.target_user.save()

        self.client.login(username='boss', password='Password123!')
        response = self.client.post(self.manage_url, {
            'user_id': self.target_user.pk,
            'action': 'revoke',
        })
        self.assertRedirects(response, self.manage_url)

        self.target_user.refresh_from_db()
        self.assertFalse(self.target_user.is_staff)

