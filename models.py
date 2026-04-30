from datetime import datetime


class Employee:
    def __init__(self, username, full_name, role="employee"):
        self.username = username
        self.full_name = full_name
        self.role = role


class Product:
    def __init__(
        self,
        name,
        category,
        quantity,
        price,
        aisle,
        shelf,
        reorder_level,
        sold_count=0,
        created_at=None,
        last_sale_at=None,
        product_id=None,
    ):
        self.id = product_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = price
        self.aisle = aisle
        self.shelf = shelf
        self.reorder_level = reorder_level
        self.sold_count = sold_count
        self.created_at = created_at or datetime.now()
        self.last_sale_at = last_sale_at

    def to_document(self):
        return {
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "aisle": self.aisle,
            "shelf": self.shelf,
            "reorder_level": self.reorder_level,
            "sold_count": self.sold_count,
            "created_at": self.created_at,
            "last_sale_at": self.last_sale_at,
        }

    def get_location(self):
        return f"Aisle {self.aisle}, Shelf {self.shelf}"


def product_from_document(document):
    return Product(
        name=document["name"],
        category=document.get("category", "General"),
        quantity=int(document.get("quantity", 0)),
        price=float(document.get("price", 0)),
        aisle=document.get("aisle", "Unknown"),
        shelf=document.get("shelf", "Unknown"),
        reorder_level=int(document.get("reorder_level", 5)),
        sold_count=int(document.get("sold_count", 0)),
        created_at=document.get("created_at") or datetime.now(),
        last_sale_at=document.get("last_sale_at"),
        product_id=str(document["_id"]),
    )
