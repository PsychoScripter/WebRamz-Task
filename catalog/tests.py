from django.test import TestCase
from django.core.exceptions import ValidationError
from catalog.models import Product, Category, Tag
from catalog.services import process_order


class ProcessOrderTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Electronics")
        self.p1 = Product.objects.create(
            name="Laptop", description="", price=1000, stock=10, category=self.cat
        )
        self.p2 = Product.objects.create(
            name="Phone", description="", price=500, stock=2, category=self.cat
        )

    def test_success_deducts_all(self):
        result = process_order([
            {"product_id": self.p1.id, "quantity": 3},
            {"product_id": self.p2.id, "quantity": 2},
        ])
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual(self.p1.stock, 7)
        self.assertEqual(self.p2.stock, 0)
        # Output structure
        result_sorted = sorted(result, key=lambda x: x["product_id"])
        self.assertEqual(result_sorted, [
            {"product_id": self.p1.id, "new_stock": 7},
            {"product_id": self.p2.id, "new_stock": 0},
        ])

    def test_rollback_when_one_item_insufficient(self):
        # We request more than the available amount for p2 until it fails.
        with self.assertRaises(ValidationError):
            process_order([
                {"product_id": self.p1.id, "quantity": 5},
                {"product_id": self.p2.id, "quantity": 3},  # Only 2 available.
            ])

        # Both products should remain unchanged (full rollback)
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual(self.p1.stock, 10)
        self.assertEqual(self.p2.stock, 2)

    def test_merge_duplicate_lines_for_same_product(self):
        # Two lines for one product must be added together (3+2=5)
        result = process_order([
            {"product_id": self.p1.id, "quantity": 3},
            {"product_id": self.p1.id, "quantity": 2},
        ])
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 5)
        self.assertEqual(result, [{"product_id": self.p1.id, "new_stock": 5}])

    def test_validation_errors(self):
        with self.assertRaises(ValidationError):
            process_order([{"product_id": self.p1.id, "quantity": 0}])  # qty must be > 0
        with self.assertRaises(ValidationError):
            process_order([{"product_id": 99999, "quantity": 1}])       # Product does not exist.
