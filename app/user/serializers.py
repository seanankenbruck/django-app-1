"""
Serializers for user API.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        username = attrs.get('username')
        password = attrs.get('password')
        # Attempt to authenticate with given credentials
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )

        # If credentials not valid, return error
        if not user:
            msg = _('Unable to authenticate with given credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        # If auth successful, return user
        attrs['user'] = user
        return attrs
