# shop/api/views.py
from rest_framework import viewsets, permissions
from shop.models import Store, Product, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer

# Vendor only access for creating/updating stores/products
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]  # optionally check vendor role
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # assign store owner automatically

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]  # optionally check vendor role
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Ensure vendor owns the store
        store = serializer.validated_data['store']
        if store.owner != self.request.user:
            raise PermissionError("You do not own this store")
        serializer.save()

class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]  # everyone can view
