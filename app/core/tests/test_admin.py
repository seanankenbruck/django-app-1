"""
Tests for Django admin interface.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class DjangoAdminTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and test client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username='Super User',
            email='superuser@example.com',
            password='password@123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            username='Test User',
            email='testuser@example.com',
            password='123@password'
        )

    def test_users_list(self):
        """Test that users are listed."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test edit user page functionality."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test create user page."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
