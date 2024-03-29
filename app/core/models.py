"""
Database models
"""
import uuid
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def product_image_file_path(instance, filename):
    """Generate file path for new product image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'product', filename)


class UserManager(BaseUserManager):
    """Manager class for users"""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create, save and return user"""
        # Validate username
        if not username:
            raise ValueError('User must have valid username.')
        # Validate email
        if not email:
            raise ValueError('User must have valid email address.')
        # Create user
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password):
        """Create and return new superuser"""
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


class Product(models.Model):
    """Product model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(null=True, upload_to=product_image_file_path)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering products"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
