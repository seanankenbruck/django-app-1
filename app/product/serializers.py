"""
Product Serializers
"""
from rest_framework import serializers
from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'image_title', 'image']
        read_only_fields = ['id']


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail"""

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description']
