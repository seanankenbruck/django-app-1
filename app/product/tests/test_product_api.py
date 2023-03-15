"""
Tests for Product APIs
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Product
from product.serializers import (
    ProductSerializer,
    ProductDetailSerializer
)


PRODUCTS_URL = reverse('product:product-list')

def detail_url(product_id):
    """Return url for specific product"""
    return reverse('product:product-detail', args=[product_id])


def create_product(user, **params):
    """Create and return a product"""
    defaults = {
        'title' : 'Sample Product',
        'description': 'Test product model',
        'price' : Decimal('0.01'),
        'image_title' : 'Image',
        'image' : 'image.jpg'
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
            'title' : 'Sample Product',
            'description': 'Test product API',
            'price' : Decimal('0.01'),
            'image_title' : 'Image',
            'image' : 'image.jpg'
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_patch_product(self):
        """Partial update of a product"""
        original_image = 'image1.jpeg'
        product = create_product(
            user=self.user,
            title='Patch product test',
            image=original_image
        )

        payload = {
            'image': 'image1.jpg',
            'title': 'Product patched'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.image, payload['image'])
        self.assertEqual(product.title, payload['title'])
        self.assertEqual(product.user, self.user)

    def test_put_product(self):
        """Full update of a product"""
        product = create_product(
            user=self.user
        )

        payload = {
            'title' : 'Product udpated',
            'description': 'Updated with a PUT',
            'price' : Decimal('0.02'),
            'image_title' : 'Image2',
            'image' : 'image2.jpg'
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.user, self.user)

    def test_updating_user_returns_error(self):
        """Test changing user on recipe returns error"""
        rogue_user = create_user(username='rogue1', email='rogue@example.com', password='test123')
        product = create_product(
            user=self.user
        )
        payload = {
            'user': rogue_user.id,
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload)
        product.refresh_from_db()
        self.assertEqual(product.user, self.user)

    def test_delete_recipe(self):
        """Test ability to delete recipe"""
        product = create_product(
            user=self.user
        )
        url = detail_url(product.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_other_user_product_error(self):
        """Test attempt to delete other user product returns error"""
        new_user = create_user(username='user2', email='user2@example.com', password='test123')
        product = create_product(
            user=new_user
        )
        url = detail_url(product.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=product.id).exists())
