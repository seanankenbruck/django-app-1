"""
Product API Views
"""
from rest_framework import (
    viewsets,
    mixins,
    status
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import (
    Product,
    Tag
)
from product import serializers


class ProductViewSet(viewsets.ModelViewSet):
    """View for product APIs"""
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve products for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return serializer class for request"""
        if self.action == 'list':
            return serializers.ProductSerializer
        # elif self.action == 'upload_image':
        #     return serializers.ProductImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new product"""
        serializer.save(user=self.request.user)

    # @action(methods=['POST'], detail=True, url_path='upload-image')
    # def upload_image(self, request, pk=None):
    #     """Upload an image to product"""
    #     product = self.get_object()
    #     serializer = self.get_serializer(product, data=request.data)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Views for managing tags"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter tags for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
