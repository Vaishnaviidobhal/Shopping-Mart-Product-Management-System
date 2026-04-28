from datetime import datetime, timezone
from uuid import uuid4

from shopping_mart.models.product import Product


class InventoryService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def add_product(self, data):
        product = Product(
            sku=self._product_sku(data),
            name=data["name"].strip(),
            category=data["category"].strip() or "General",
            quantity=int(data["quantity"]),
            price=float(data["price"]),
            aisle=data["aisle"].strip(),
            shelf=data["shelf"].strip(),
            reorder_level=int(data.get("reorder_level") or 5),
        )
        self._validate_product(product)
        self.product_repository.create(product)

    def update_product(self, sku, data):
        changes = {
            "name": data["name"].strip(),
            "category": data["category"].strip() or "General",
            "quantity": int(data["quantity"]),
            "price": float(data["price"]),
            "aisle": data["aisle"].strip(),
            "shelf": data["shelf"].strip(),
            "reorder_level": int(data.get("reorder_level") or 5),
        }
        self._validate_values(changes)
        self.product_repository.update(sku, changes)

    def delete_product(self, sku):
        self.product_repository.delete(sku)

    def record_sale(self, sku, amount):
        self.product_repository.record_sale(sku, int(amount))

    def all_products(self):
        return self.product_repository.find_all()

    def sold_out_products(self):
        return [product for product in self.all_products() if product.quantity <= 0]

    def low_stock_products(self):
        return [
            product
            for product in self.all_products()
            if 0 < product.quantity <= product.reorder_level
        ]

    def high_demand_products(self):
        products = []
        now = datetime.now(timezone.utc)
        for product in self.all_products():
            daily_sales = self.demand_score(product)
            if product.sold_count >= 10 and (daily_sales >= 2 or self.is_low_stock(product)):
                products.append((daily_sales, product))

        products.sort(key=lambda item: (item[0], item[1].sold_count), reverse=True)
        return [product for _, product in products]

    def dashboard_counts(self):
        products = self.all_products()
        return {
            "total": len(products),
            "sold_out": len([product for product in products if product.quantity <= 0]),
            "low_stock": len(
                [
                    product
                    for product in products
                    if 0 < product.quantity <= product.reorder_level
                ]
            ),
            "high_demand": len(self.high_demand_products()),
        }

    def demand_score(self, product):
        now = datetime.now(timezone.utc)
        days_live = max((now - self._aware(product.created_at)).days, 1)
        return product.sold_count / days_live

    def stock_status(self, product):
        if product.quantity <= 0:
            return "Sold Out"
        if self.is_low_stock(product):
            return "Low Stock"
        if product in self.high_demand_products():
            return "High Demand"
        return "In Stock"

    def is_low_stock(self, product):
        return 0 < product.quantity <= product.reorder_level

    def _validate_product(self, product):
        if not product.sku:
            raise ValueError("SKU is required.")
        values = product.to_document()
        self._validate_values(values)

    def _validate_values(self, values):
        if not values["name"]:
            raise ValueError("Product name is required.")
        if values["quantity"] < 0:
            raise ValueError("Quantity cannot be negative.")
        if values["price"] < 0:
            raise ValueError("Price cannot be negative.")
        if values["reorder_level"] < 0:
            raise ValueError("Reorder level cannot be negative.")
        if not values["aisle"] or not values["shelf"]:
            raise ValueError("Aisle and shelf are required.")

    def _aware(self, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    def _product_sku(self, data):
        if data.get("sku"):
            return data["sku"].upper().strip()

        name_part = "".join(
            character for character in data["name"].upper() if character.isalnum()
        )[:4]
        if not name_part:
            name_part = "ITEM"
        return f"{name_part}-{uuid4().hex[:6].upper()}"
