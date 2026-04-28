from datetime import datetime, timezone

from shopping_mart.models.product import Product


class ProductRepository:
    def __init__(self, collection):
        self.collection = collection

    def count(self):
        return self.collection.count_documents({})

    def find_all(self):
        documents = self.collection.find({}).sort("name", 1)
        return [Product.from_document(document) for document in documents]

    def find_by_sku(self, sku):
        document = self.collection.find_one({"sku": sku.upper().strip()})
        return Product.from_document(document) if document else None

    def create(self, product):
        self.collection.insert_one(product.to_document())

    def update(self, sku, changes):
        self.collection.update_one({"sku": sku.upper().strip()}, {"$set": changes})

    def delete(self, sku):
        self.collection.delete_one({"sku": sku.upper().strip()})

    def record_sale(self, sku, amount):
        product = self.find_by_sku(sku)
        if product is None:
            raise ValueError("Product not found.")
        if amount <= 0:
            raise ValueError("Sale quantity must be greater than zero.")
        if product.quantity < amount:
            raise ValueError("Not enough stock available.")

        self.collection.update_one(
            {"sku": product.sku},
            {
                "$inc": {"quantity": -amount, "sold_count": amount},
                "$set": {"last_sale_at": datetime.now(timezone.utc)},
            },
        )
