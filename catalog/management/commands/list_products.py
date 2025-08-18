from django.core.management.base import BaseCommand
from django.db.models import Avg, Prefetch
from catalog.models import Product, Tag

"""
This Django management command retrieves products from the database and prints out their details, including:

0  Name and Price of the product
0  Category name
0  Tags associated with the product
0  Average rating from reviews

Key techniques used to optimize database queries and avoid the N+1 query problem:
1. select_related("category") – Fetches the related category of each product in the same SQL query 
(avoiding separate queries per product).

2. prefetch_related(Prefetch(...)) – Fetches all related tags for all products in one query and attaches 
them to the products.

3. annotate(avg_rating=Avg("reviews__rating")) – Calculates the average rating in the database itself 
rather than looping through reviews in Python.

This approach ensures the database is queried efficiently, preventing one query per related object (N+1 problem).
"""
class Command(BaseCommand):
    def handle(self, *args, **options):
        products = (
            Product.objects
            .select_related("category")
            .prefetch_related(
                Prefetch("tags", queryset=Tag.objects.only("name"))
            )
            .annotate(avg_rating=Avg("reviews__rating"))
        )

        for product in products:
            avg_rating = product.avg_rating if product.avg_rating else "No points"
            tag_names = ", ".join(product.tags.values_list("name", flat=True))
            self.stdout.write(
                f"Name: {product.name} | "
                f"Price: {product.price} | "
                f"Category: {product.category.name} | "
                f"Tags: {tag_names} | "
                f"Avg Rating: {avg_rating}"
            )
