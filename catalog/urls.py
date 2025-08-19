# catalog/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, TagViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r'reviews', ReviewViewSet)
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = router.urls
