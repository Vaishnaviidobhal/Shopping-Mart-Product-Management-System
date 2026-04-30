import tkinter as tk
from tkinter import messagebox

from auth import AuthService
from database import MongoDB
from inventory import InventoryService, ProductRepository
from ui.dashboard_window import DashboardWindow
from ui.login_window import LoginWindow


def show_dashboard(root, inventory_service, employee):
    DashboardWindow(root, employee, inventory_service)


def main():
    root = tk.Tk()
    root.withdraw()

    db = MongoDB()
    product_repository = ProductRepository(db.products)
    auth_service = AuthService()
    inventory_service = InventoryService(product_repository)

    try:
        db.ping()
    except Exception as exc:
        messagebox.showerror(
            "MongoDB connection failed",
            "Start MongoDB, then run this project again.\n\n"
            f"Details: {exc}",
        )
        root.destroy()
        return

    LoginWindow(
        root,
        auth_service,
        lambda employee: show_dashboard(root, inventory_service, employee),
    )
    root.mainloop()


if __name__ == "__main__":
    main()
