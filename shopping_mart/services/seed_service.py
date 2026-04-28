from shopping_mart.models.product import Product
from shopping_mart.models.employee import Employee
from shopping_mart.utils.security import hash_password


class SeedService:
    def __init__(self, auth_service, inventory_service):
        self.auth_service = auth_service
        self.inventory_service = inventory_service

    def ensure_default_employee(self):
        employee = Employee(
            username=self.auth_service.PERMANENT_USERNAME,
            password_hash=hash_password(self.auth_service.PERMANENT_PASSWORD),
            full_name=self.auth_service.PERMANENT_FULL_NAME,
            role=self.auth_service.PERMANENT_ROLE,
        )
        self.auth_service.employee_repository.upsert(employee)

    def ensure_demo_products(self):
        if self.inventory_service.product_repository.count() > 0:
            return

        demo_products = [
            Product("RCE-101", "Basmati Rice 5kg", "Grocery", 4, 620, "1", "B2", 8, 35),
            Product("MLK-220", "Full Cream Milk 1L", "Dairy", 0, 68, "2", "A1", 12, 52),
            Product("SOAP-09", "Herbal Bath Soap", "Personal Care", 28, 45, "5", "C4", 10, 8),
            Product("OIL-330", "Sunflower Oil 1L", "Grocery", 7, 155, "1", "D1", 10, 26),
            Product("BIS-450", "Chocolate Biscuits", "Snacks", 45, 30, "3", "B1", 15, 41),
        ]
        for product in demo_products:
            self.inventory_service.product_repository.create(product)
