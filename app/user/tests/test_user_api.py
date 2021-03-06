"""
Test the user api.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
CURRENT_USER_URL = reverse('user:current-user')


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test public endpoints of user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create user is successful."""
        payload = {
            'username': 'test1',
            'email': 'test1@example.com',
            'password': 'password123!',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_username_already_exist(self):
        """Test error returned if username already in use."""
        payload = {
            'username': 'test1',
            'email': 'test1@example.com',
            'password': 'password123!',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_already_exists(self):
        """Test error returned if email already in use."""
        payload = {
            'username': 'test1',
            'email': 'test1@example.com',
            'password': 'password123!',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test error returned if password too short."""
        payload = {
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'pw',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        )
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        """Test generate token with valid credentials."""
        user_details = {
            'username': 'test',
            'email': 'test@example.com',
            'password': 'password123!',
        }
        create_user(**user_details)

        payload = {
            'username': user_details['username'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        user_details = {
            'username': 'test',
            'email': 'test@example.com',
            'password': 'password123!',
        }
        create_user(**user_details)

        payload = {
            'username': user_details['username'],
            'password': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_token_bad_creds(self):
        """Test returns error for invalid credentials"""
        user_details = {
            'username': 'test',
            'email': 'test@example.com',
            'password': 'password123!',
        }
        create_user(**user_details)

        payload = {
            'username': user_details['username'],
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_current_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(CURRENT_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            username='test',
            email='test@example.com',
            password='password123!',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def get_profile_url_success(self):
        """Test retrive profile for logged in user."""
        res = self.client.get(CURRENT_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'username': self.user.username,
            'email': self.user.email,
        })

    def test_update_user_profile(self):
        """Test update profile for current user"""
        payload = {
            'username': 'Updated name',
            'password': 'password2'
        }

        res = self.client.patch(CURRENT_USER_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
