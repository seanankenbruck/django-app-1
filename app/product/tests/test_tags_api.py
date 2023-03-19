"""
Test for the tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Tag,
    Product
)
from product.serializers import TagSerializer

TAGS_URL = reverse('product:tag-list')


def detail_url(tag_id):
    """Create and return tag detail url"""
    return reverse('product:tag-detail', args=[tag_id])


def create_tag(user, **params):
    """Create and return a tag"""
    defaults = {
        'name': 'Generic'
    }
    defaults.update(params)

    tag = Tag.objects.create(user=user, **defaults)
    return tag


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to use API"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTagsAPITests(TestCase):
    """Test authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='test1',
            email='test@example.com',
            password='password@1234',
        )
        self.client.force_authenticate(self.user)

    def test_get_tags(self):
        """Test ability to retrieve tags"""
        create_tag(user=self.user, name='Tag1')
        create_tag(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_filtered_by_user(self):
        """Test tag list filtered by authenticated user"""
        new_user = create_user(
            username='test2',
            email='test2@example.com',
            password='password@1234',
        )
        create_tag(user=new_user, name='Tag1')
        tag = create_tag(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test abiltiy to update tag"""
        tag = Tag.objects.create(user=self.user, name='Tag1')

        payload = {'name': 'Tag1Update'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test abiltiy to delete tag"""
        tag = Tag.objects.create(user=self.user, name='Tag1')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())
