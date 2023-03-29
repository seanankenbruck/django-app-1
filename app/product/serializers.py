"""
Product Serializers
"""
from rest_framework import serializers
from core.models import (
    Product,
    Tag
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, product):
        """Helper function for getting or creating tags"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            product.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a product"""
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        self._get_or_create_tags(tags, product)

        return product

    def update(self, instance, validated_data):
        """Update a product"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail"""

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for images"""

    class Meta:
        model = Product
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
