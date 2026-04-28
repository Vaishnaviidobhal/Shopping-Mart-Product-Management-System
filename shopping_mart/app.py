import tkinter as tk
from tkinter import messagebox

from shopping_mart.config import AppConfig
from shopping_mart.database.mongo_client import MongoDB
from shopping_mart.repositories.employee_repository import EmployeeRepository
from shopping_mart.repositories.product_repository import ProductRepository
from shopping_mart.services.auth_service import AuthService
from shopping_mart.services.inventory_service import InventoryService
from shopping_mart.services.seed_service import SeedService
from shopping_mart.ui.dashboard_window import DashboardWindow
from shopping_mart.ui.login_window import LoginWindow


class ShoppingMartApp:
    def __init__(self):
        self.config = AppConfig()
        self.root = tk.Tk()
        self.root.withdraw()

        self.db = MongoDB(self.config)
        self.employee_repository = EmployeeRepository(self.db.employees)
        self.product_repository = ProductRepository(self.db.products)
        self.auth_service = AuthService(self.employee_repository)
        self.inventory_service = InventoryService(self.product_repository)
        self.seed_service = SeedService(self.auth_service, self.inventory_service)

    def run(self):
        try:
            self.db.ping()
            self.seed_service.ensure_default_employee()
            self.seed_service.ensure_demo_products()
        except Exception as exc:
            messagebox.showerror(
                "MongoDB connection failed",
                "Start MongoDB, then run this project again.\n\n"
                f"Details: {exc}",
            )
            self.root.destroy()
            return

        self.show_login()
        self.root.mainloop()

    def show_login(self):
        LoginWindow(
            self.root,
            self.auth_service,
            self.show_dashboard,
        )

    def show_dashboard(self, employee):
        DashboardWindow(self.root, employee, self.inventory_service)
