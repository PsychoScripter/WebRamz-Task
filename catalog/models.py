from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Prefetch


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subcategories',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def with_related_data(self):
        return self.select_related("category").prefetch_related(
            Prefetch("tags", queryset=Tag.objects.only("name"))
        ).annotate(average_rating=Avg("reviews__rating"))

class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', related_name="products", on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', related_name="products")

    objects = ProductQuerySet.as_manager()


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="reviews",
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} - {self.rating} stars"