from typing import List, Dict
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from catalog.models import Product


def _normalize_items(order_items: List[Dict]) -> Dict[int, int]:
    """
    Normalizes inputs:
    - Sums the value if a product_id is duplicated
    - Validates the value of the quantity (>0)
    Output: {product_id: total_quantity}
    """
    qty_by_id: Dict[int, int] = {}
    for item in order_items or []:
        pid = item.get("product_id")
        qty = item.get("quantity")
        if not isinstance(pid, int):
            raise ValidationError({"product_id": "Invalid or missing product_id."})
        if not isinstance(qty, int) or qty <= 0:
            raise ValidationError({"quantity": "Quantity must be a positive integer."})
        qty_by_id[pid] = qty_by_id.get(pid, 0) + qty
    return qty_by_id


@transaction.atomic
def process_order(order_items: List[Dict]) -> List[Dict]:
    """
    order_items: [{"product_id": int, "quantity": int}, ...]
    - If the stock of any product is not enough, it throws a ValidationError and the transaction is rolled back.
    - If it is enough, the stock of all products is atomically reduced.
    Output: A list of the result of each product: [{"product_id": id, "new_stock": int}, ...]
    """
    qty_by_id = _normalize_items(order_items)
    if not qty_by_id:
        return []

    product_ids = list(qty_by_id.keys())

    # Row locks to prevent concurrent threads
    products = list(
        Product.objects
        .select_for_update()
        .only("id", "name", "stock")
        .filter(id__in=product_ids)
    )

    # Existence of all products
    if len(products) != len(product_ids):
        missing = set(product_ids) - {p.id for p in products}
        raise ValidationError({"not_found": sorted(missing)})

    # Inventory adequacy check
    insufficient = []
    for p in products:
        requested = qty_by_id[p.id]
        if p.stock < requested:
            insufficient.append({
                "product_id": p.id,
                "name": p.name,
                "requested": requested,
                "available": p.stock,
            })

    if insufficient:
        raise ValidationError({"insufficient_stock": insufficient})

    # Atomically subtract inventory with F(); each row is a safe UPDATE
    for p in products:
        Product.objects.filter(id=p.id).update(stock=F("stock") - qty_by_id[p.id])

    # Output: New status (for quick display; if you want accuracy, do refresh_from_db)
    return [{"product_id": p.id, "new_stock": p.stock - qty_by_id[p.id]} for p in products]
