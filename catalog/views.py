from rest_framework import viewsets, filters
from catalog.models import Product, Tag, Category
from .permissions import IsAdminOrReadOnly
from .serializers import ProductSerializer, CategorySerializer, TagSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema

@extend_schema_view(
    list=extend_schema(description="Retrieve a list of products. Anyone can read, only admins can modify."),
    retrieve=extend_schema(description="Retrieve single product details")
)
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category__name', 'tags__name']
    ordering_fields = ['price', 'name']

    def get_queryset(self):
        queryset = Product.objects.with_related_data()

        category_name = self.request.query_params.get("category")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        tags_param = self.request.query_params.get("tags")
        if tags_param:
            tags_list = [t.strip() for t in tags_param.split(",")]
            queryset = queryset.filter(tags__name__in=tags_list).distinct()

        return queryset

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]