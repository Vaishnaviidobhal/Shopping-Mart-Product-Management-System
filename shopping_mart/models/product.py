from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Product:
    sku: str
    name: str
    category: str
    quantity: int
    price: float
    aisle: str
    shelf: str
    reorder_level: int
    sold_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_sale_at: Optional[datetime] = None

    def to_document(self):
        return {
            "sku": self.sku,
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

    @classmethod
    def from_document(cls, document):
        return cls(
            sku=document["sku"],
            name=document["name"],
            category=document.get("category", "General"),
            quantity=int(document.get("quantity", 0)),
            price=float(document.get("price", 0)),
            aisle=document.get("aisle", "Unknown"),
            shelf=document.get("shelf", "Unknown"),
            reorder_level=int(document.get("reorder_level", 5)),
            sold_count=int(document.get("sold_count", 0)),
            created_at=document.get("created_at") or datetime.now(timezone.utc),
            last_sale_at=document.get("last_sale_at"),
        )

    @property
    def location(self):
        return f"Aisle {self.aisle}, Shelf {self.shelf}"
