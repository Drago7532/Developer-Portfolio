from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import StoreViewSet, ProductViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]