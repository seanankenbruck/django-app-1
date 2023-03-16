"""
Test django models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email(self):
        """Test ability to create user with username and email."""
        username = 'test1'
        email = 'test@example.com'
        password = 'password@1234'
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_user_email(self):
        """Test email normalization."""
        email_list = [
            ["user1", "user1@EXAMPLE.com", "user1@example.com"],
            ["user2", "User2@Example.com", "User2@example.com"],
            ["user3", "USER3@EXAMPLE.COM", "USER3@example.com"],
        ]
        for name, email, normalized in email_list:
            user = get_user_model().objects.create_user(
                name,
                email,
                'password123'
            )
            self.assertEqual(user.email, normalized)

    def test_empty_username_throws_error(self):
        """Test that creating user without a username throws error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                '',
                'user1@example.com',
                'password123'
            )

    def test_empty_email_throws_error(self):
        """Test that creating user without an email throws error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('user1', '', 'password123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'superuser1',
            'superuser@example.com',
            'password@123!'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_product(self):
        """Test creating a product is successful."""
        username = 'test1'
        email = 'test@example.com'
        password = 'password@1234'
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        product = models.Product.objects.create(
            user=user,
            title="Sample Product",
            description="Test product model",
            price=Decimal('5.00'),
            image_title="Image1",
            image="image.jpg"
        )

        self.assertEqual(str(product), product.title)
