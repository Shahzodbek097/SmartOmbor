from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    OmborMovementViewSet,
    OrderViewSet,
)


router = DefaultRouter()

router.register("categories",CategoryViewSet,basename="category")
router.register("products",ProductViewSet,basename="product")
router.register("movements",OmborMovementViewSet,basename="movement")
router.register("orders",OrderViewSet,basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
