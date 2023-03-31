"""
Tests for Product APIs
"""
from decimal import Decimal
import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Product,
    Tag
)
from product.serializers import (
    ProductSerializer,
    ProductDetailSerializer
)


PRODUCTS_URL = reverse('product:product-list')


def detail_url(product_id):
    """Return url for specific product"""
    return reverse('product:product-detail', args=[product_id])


def image_upload_url(product_id):
    """Create and return an image upload url"""
    return reverse('product:product-upload-image', args=[product_id])


def create_product(user, **params):
    """Create and return a product"""
    defaults = {
        'title': 'Sample Product',
        'description': 'Test product model',
        'price': Decimal('0.01')
    }
    defaults.update(params)

    product = Product.objects.create(user=user, **defaults)
    return product


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


class PublicProductAPITests(TestCase):
    """Test unauthenticated API requests"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to use API"""
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProductAPITests(TestCase):
    """Test authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='test1',
            email='test@example.com',
            password='password@1234',
        )
        self.client.force_authenticate(self.user)

    def test_get_products(self):
        """Test ability to retrieve products"""
        create_product(user=self.user)
        create_product(user=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_products_filters_by_user(self):
        """Test product list filtered by authenticated user"""
        new_user = create_user(
            username='test2',
            email='test2@example.com',
            password='password@1234',
        )
        create_product(user=new_user)
        create_product(user=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_product_detail(self):
        """Test product detail resource"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test abilty to create a new product entry"""
        payload = {
            'title': 'Sample Product',
            'description': 'Test product API',
            'price': Decimal('0.01')
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_patch_product(self):
        """Partial update of a product"""
        product = create_product(
            user=self.user,
            title='Patch product test',
        )

        payload = {
            'title': 'Product patched'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])
        self.assertEqual(product.user, self.user)

    def test_put_product(self):
        """Full update of a product"""
        product = create_product(
            user=self.user
        )

        payload = {
            'title': 'Product udpated',
            'description': 'Updated with a PUT',
            'price': Decimal('0.02')
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_updating_user_returns_error(self):
        """Test changing user on product returns error"""
        rogue_user = create_user(
            username='rogue1',
            email='rogue@example.com',
            password='test123'
        )
        product = create_product(
            user=self.user
        )
        payload = {
            'user': rogue_user.id,
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload)
        product.refresh_from_db()
        self.assertIsNotNone(res)
        self.assertEqual(product.user, self.user)

    def test_delete_product(self):
        """Test ability to delete product"""
        product = create_product(
            user=self.user
        )
        url = detail_url(product.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_other_user_product_error(self):
        """Test attempt to delete other user product returns error"""
        new_user = create_user(
            username='user2',
            email='user2@example.com',
            password='test123'
        )
        product = create_product(
            user=new_user
        )
        url = detail_url(product.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_create_product_with_new_tag(self):
        """Test creating a product with new tag"""
        payload = {
            'title': 'Sample Product',
            'description': 'Test product tags',
            'price': Decimal('0.01'),
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}]
        }
        res = self.client.post(PRODUCTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        products = Product.objects.filter(user=self.user)
        self.assertEqual(products.count(), 1)
        product = products[0]
        self.assertEqual(product.tags.count(), 2)
        for tag in payload['tags']:
            exists = product.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_product_with_existing_tag(self):
        """Test creating a product with existing tag"""
        test_tag = Tag.objects.create(user=self.user, name='TestTag1')
        payload = {
            'title': 'Sample Product',
            'description': 'Test product tags',
            'price': Decimal('0.01'),
            'tags': [{'name': 'TestTag1'}, {'name': 'TestTag2'}]
        }
        res = self.client.post(PRODUCTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        products = Product.objects.filter(user=self.user)
        self.assertEqual(products.count(), 1)
        product = products[0]
        self.assertEqual(product.tags.count(), 2)
        self.assertIn(test_tag, product.tags.all())
        for tag in payload['tags']:
            exists = product.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a product."""
        product = create_product(user=self.user)

        payload = {'tags': [{'name': 'PatchTag'}]}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='PatchTag')
        self.assertIn(new_tag, product.tags.all())

    def test_update_product_assign_tag(self):
        """Test assign existing tag when updating a product"""
        tag = Tag.objects.create(user=self.user, name='ProductUpdate')
        product = create_product(user=self.user)
        product.tags.add(tag)

        new_tag = Tag.objects.create(user=self.user, name='ProductUpdate2')
        payload = {'tags': [{'name': 'ProductUpdate2'}]}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(new_tag, product.tags.all())
        self.assertNotIn(tag, product.tags.all())

    def test_clear_product_tags(self):
        """Test clear all tags for a product"""
        tag = Tag.objects.create(user=self.user, name='DeleteThis')
        product = create_product(user=self.user)
        product.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product.tags.count(), 0)

    def test_filter_tags(self):
        """Test filtering tags"""
        product1 = create_product(user=self.user, title='Product 1')
        product2 = create_product(user=self.user, title='Product 2')
        tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        tag2 = Tag.objects.create(user=self.user, name='Tag 2')
        product1.tags.add(tag1)
        product2.tags.add(tag2)
        product3 = create_product(user=self.user, title='Product3')

        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(PRODUCTS_URL, params)

        serialized1 = ProductSerializer(product1)
        serialized2 = ProductSerializer(product2)
        serialized3 = ProductSerializer(product3)
        self.assertIn(serialized1.data, res.data)
        self.assertIn(serialized2.data, res.data)
        self.assertNotIn(serialized3.data, res.data)


class ImageUploadTests(TestCase):
    """Test for uploading images"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='test1',
            email='test@example.com',
            password='password@1234',
        )
        self.client.force_authenticate(self.user)
        self.product = create_product(user=self.user)

    def tearDown(self):
        self.product.image.delete()

    def test_upload_image(self):
        """Test upload of image to product"""
        url = image_upload_url(self.product.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.product.image.path))

    def test_image_upload_bad_request(self):
        """Test bad request for image upload"""
        url = image_upload_url(self.product.id)
        payload = {'image': 'thisisnotanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
