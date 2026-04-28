import tkinter as tk
from tkinter import messagebox, ttk

from pymongo.errors import DuplicateKeyError

from shopping_mart.ui import styles


class ProductDialog(tk.Toplevel):
    def __init__(self, master, title, on_submit, product=None):
        super().__init__(master)
        self.on_submit = on_submit
        self.product = product
        self.entries = {}

        self.title(title)
        self.configure(bg=styles.INPUT_PANEL)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._build(title)
        self._fill_product()
        self.entries["name"].focus_set()

    def _build(self, title):
        shell = tk.Frame(self, bg=styles.INPUT_PANEL, padx=24, pady=20)
        shell.pack(fill="both", expand=True)

        tk.Label(
            shell,
            text=title,
            font=styles.TITLE_FONT,
            bg=styles.INPUT_PANEL,
            fg=styles.ACCENT,
        ).pack(anchor="w")

        fields = [
            ("name", "Item Name"),
            ("category", "Category"),
            ("quantity", "Quantity"),
            ("price", "Price"),
            ("aisle", "Aisle"),
            ("shelf", "Shelf"),
        ]
        form = tk.Frame(shell, bg=styles.INPUT_PANEL)
        form.pack(fill="x", pady=(14, 10))
        for key, label in fields:
            tk.Label(form, text=label, font=styles.FONT, bg=styles.INPUT_PANEL).pack(anchor="w")
            entry = tk.Entry(form, font=styles.FONT, width=36)
            entry.pack(fill="x", pady=(3, 9))
            self.entries[key] = entry

        row = tk.Frame(shell, bg=styles.INPUT_PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Button(
            row,
            text="Save",
            font=styles.FONT,
            bg=styles.SUCCESS,
            fg="white",
            activebackground=styles.SUCCESS,
            activeforeground="white",
            command=self._submit,
        ).pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="Cancel",
            font=styles.FONT,
            bg=styles.WARNING,
            fg="white",
            activebackground=styles.WARNING,
            activeforeground="white",
            command=self.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(10, 0))

    def _fill_product(self):
        if self.product is None:
            return
        values = {
            "name": self.product.name,
            "category": self.product.category,
            "quantity": self.product.quantity,
            "price": f"{self.product.price:.2f}",
            "aisle": self.product.aisle,
            "shelf": self.product.shelf,
        }
        for key, value in values.items():
            self.entries[key].insert(0, str(value))

    def _submit(self):
        values = {key: entry.get() for key, entry in self.entries.items()}
        if self.on_submit(values):
            self.destroy()


class SaleDialog(tk.Toplevel):
    def __init__(self, master, product, on_submit):
        super().__init__(master)
        self.product = product
        self.on_submit = on_submit

        self.title("Record Sale")
        self.configure(bg=styles.OUTPUT_PANEL)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        shell = tk.Frame(self, bg=styles.OUTPUT_PANEL, padx=24, pady=20)
        shell.pack(fill="both", expand=True)

        tk.Label(
            shell,
            text="Record Sale",
            font=styles.TITLE_FONT,
            bg=styles.OUTPUT_PANEL,
            fg=styles.TEAL,
        ).pack(anchor="w")
        tk.Label(
            shell,
            text=f"{product.name} - Available: {product.quantity}",
            font=styles.FONT,
            bg=styles.OUTPUT_PANEL,
            fg=styles.MUTED,
        ).pack(anchor="w", pady=(4, 14))

        tk.Label(shell, text="Quantity Sold", font=styles.FONT, bg=styles.OUTPUT_PANEL).pack(anchor="w")
        self.amount_entry = tk.Entry(shell, font=styles.FONT, width=20)
        self.amount_entry.insert(0, "1")
        self.amount_entry.pack(fill="x", pady=(3, 14))
        self.amount_entry.focus_set()

        tk.Button(
            shell,
            text="Record",
            font=styles.FONT,
            bg=styles.TEAL,
            fg="white",
            activebackground=styles.TEAL,
            activeforeground="white",
            command=self._submit,
        ).pack(fill="x")

    def _submit(self):
        if self.on_submit(self.amount_entry.get()):
            self.destroy()


class DeleteDialog(tk.Toplevel):
    def __init__(self, master, product, on_confirm):
        super().__init__(master)
        self.on_confirm = on_confirm

        self.title("Delete Item")
        self.configure(bg=styles.PANEL)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        shell = tk.Frame(self, bg=styles.PANEL, padx=24, pady=20)
        shell.pack(fill="both", expand=True)
        tk.Label(
            shell,
            text="Delete Item",
            font=styles.TITLE_FONT,
            bg=styles.PANEL,
            fg=styles.DANGER,
        ).pack(anchor="w")
        tk.Label(
            shell,
            text=f"Remove {product.name} from the mart list?",
            font=styles.FONT,
            bg=styles.PANEL,
            fg=styles.TEXT,
        ).pack(anchor="w", pady=(8, 18))

        row = tk.Frame(shell, bg=styles.PANEL)
        row.pack(fill="x")
        tk.Button(
            row,
            text="Delete",
            font=styles.FONT,
            bg=styles.DANGER,
            fg="white",
            activebackground=styles.DANGER,
            activeforeground="white",
            command=self._confirm,
        ).pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="Cancel",
            font=styles.FONT,
            command=self.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(10, 0))

    def _confirm(self):
        if self.on_confirm():
            self.destroy()


class DashboardWindow(tk.Toplevel):
    COLUMNS = (
        "name",
        "category",
        "quantity",
        "price",
        "location",
        "status",
        "sold_count",
    )

    def __init__(self, master, employee, inventory_service):
        super().__init__(master)
        self.employee = employee
        self.inventory_service = inventory_service
        self.current_filter = "all"
        self.selected_sku = None
        self.search_text = tk.StringVar()

        self.title("Shopping Mart Product Management System")
        self.state("zoomed")
        self.minsize(960, 620)
        self.configure(bg=styles.BG)
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.bind("<Escape>", lambda _event: self.state("normal"))

        self._configure_tree_style()
        self._build()
        self.refresh()

    def _configure_tree_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=styles.FONT,
            rowheight=30,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=styles.TEXT,
        )
        style.configure(
            "Treeview.Heading",
            font=styles.SUBTITLE_FONT,
            background=styles.PRIMARY,
            foreground="white",
        )
        style.map("Treeview", background=[("selected", styles.TEAL)])

    def _build(self):
        header = tk.Frame(self, bg=styles.BG, padx=18, pady=14)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg=styles.BG)
        title_box.pack(side="left")
        tk.Label(
            title_box,
            text="Available Items",
            font=styles.TITLE_FONT,
            bg=styles.BG,
            fg=styles.PURPLE,
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="Select an item, then choose what you want to do",
            font=styles.FONT,
            bg=styles.BG,
            fg=styles.MUTED,
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"Signed in as {self.employee.full_name}",
            font=styles.FONT,
            bg=styles.BG,
            fg=styles.MUTED,
        ).pack(side="right")

        stats = tk.Frame(self, bg=styles.BG, padx=18)
        stats.pack(fill="x")
        self.stat_labels = {}
        for key, title, color in [
            ("total", "Total Items", styles.PRIMARY),
            ("low_stock", "Low Stock", styles.WARNING),
            ("sold_out", "Sold Out", styles.DANGER),
            ("high_demand", "High Demand", styles.SUCCESS),
        ]:
            frame = tk.Frame(
                stats,
                bg=styles.PANEL,
                padx=14,
                pady=10,
                highlightbackground=color,
                highlightthickness=2,
            )
            frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(frame, text=title, bg=styles.PANEL, fg=styles.MUTED, font=styles.FONT).pack(anchor="w")
            value = tk.Label(frame, text="0", bg=styles.PANEL, fg=color, font=("Segoe UI", 18, "bold"))
            value.pack(anchor="w")
            self.stat_labels[key] = value

        body = tk.Frame(self, bg=styles.OUTPUT_PANEL, padx=18, pady=16)
        body.pack(fill="both", expand=True, padx=18, pady=14)

        action_bar = tk.Frame(body, bg=styles.OUTPUT_PANEL)
        action_bar.pack(fill="x", pady=(0, 12))

        tk.Button(
            action_bar,
            text="Add Item",
            font=styles.FONT,
            bg=styles.SUCCESS,
            fg="white",
            activebackground=styles.SUCCESS,
            activeforeground="white",
            command=self.open_add_window,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            action_bar,
            text="Edit Selected",
            font=styles.FONT,
            bg=styles.PRIMARY,
            fg="white",
            activebackground=styles.PRIMARY,
            activeforeground="white",
            command=self.open_edit_window,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            action_bar,
            text="Record Sale",
            font=styles.FONT,
            bg=styles.TEAL,
            fg="white",
            activebackground=styles.TEAL,
            activeforeground="white",
            command=self.open_sale_window,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            action_bar,
            text="Delete Selected",
            font=styles.FONT,
            bg=styles.DANGER,
            fg="white",
            activebackground=styles.DANGER,
            activeforeground="white",
            command=self.open_delete_window,
        ).pack(side="left")

        tk.Button(
            action_bar,
            text="Refresh",
            font=styles.FONT,
            bg=styles.WARNING,
            fg="white",
            activebackground=styles.WARNING,
            activeforeground="white",
            command=self.refresh,
        ).pack(side="right")
        search_entry = tk.Entry(action_bar, textvariable=self.search_text, font=styles.FONT, width=26)
        search_entry.pack(side="right", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh())
        tk.Label(action_bar, text="Search", font=styles.FONT, bg=styles.OUTPUT_PANEL).pack(side="right", padx=(0, 6))

        filter_bar = tk.Frame(body, bg=styles.OUTPUT_PANEL)
        filter_bar.pack(fill="x", pady=(0, 12))
        for label, value, color in [
            ("All", "all", styles.PRIMARY),
            ("Low Stock", "low_stock", styles.WARNING),
            ("Sold Out", "sold_out", styles.DANGER),
            ("High Demand", "high_demand", styles.SUCCESS),
        ]:
            tk.Button(
                filter_bar,
                text=label,
                font=styles.FONT,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                command=lambda selected=value: self.set_filter(selected),
            ).pack(side="left", padx=(0, 8))

        self.tree = ttk.Treeview(body, columns=self.COLUMNS, show="headings", selectmode="browse")
        headings = {
            "name": "Item",
            "category": "Category",
            "quantity": "Available",
            "price": "Price",
            "location": "Location",
            "status": "Status",
            "sold_count": "Sold",
        }
        widths = {
            "name": 250,
            "category": 130,
            "quantity": 90,
            "price": 90,
            "location": 150,
            "status": 120,
            "sold_count": 80,
        }
        for column in self.COLUMNS:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("sold_out", foreground=styles.DANGER)
        self.tree.tag_configure("low_stock", foreground=styles.WARNING)
        self.tree.tag_configure("high_demand", foreground=styles.SUCCESS)
        self.tree.bind("<<TreeviewSelect>>", self._load_selected_product)
        self.tree.bind("<Double-1>", lambda _event: self.open_edit_window())

    def set_filter(self, selected_filter):
        self.current_filter = selected_filter
        self.refresh()

    def refresh(self):
        counts = self.inventory_service.dashboard_counts()
        for key, value in counts.items():
            self.stat_labels[key].configure(text=str(value))

        for row in self.tree.get_children():
            self.tree.delete(row)

        for product in self._filtered_products():
            status = self.inventory_service.stock_status(product)
            tag = self._row_tag(status)
            self.tree.insert(
                "",
                "end",
                iid=product.sku,
                values=(
                    product.name,
                    product.category,
                    product.quantity,
                    f"{product.price:.2f}",
                    product.location,
                    status,
                    product.sold_count,
                ),
                tags=(tag,),
            )

        if self.selected_sku not in self.tree.get_children():
            self.selected_sku = None

    def _filtered_products(self):
        if self.current_filter == "low_stock":
            products = self.inventory_service.low_stock_products()
        elif self.current_filter == "sold_out":
            products = self.inventory_service.sold_out_products()
        elif self.current_filter == "high_demand":
            products = self.inventory_service.high_demand_products()
        else:
            products = self.inventory_service.all_products()

        query = self.search_text.get().lower().strip()
        if not query:
            return products
        return [
            product
            for product in products
            if query in product.name.lower()
            or query in product.category.lower()
            or query in product.location.lower()
        ]

    def _row_tag(self, status):
        return status.lower().replace(" ", "_")

    def _load_selected_product(self, _event):
        selected = self.tree.selection()
        self.selected_sku = selected[0] if selected else None

    def _selected_product(self):
        if not self.selected_sku:
            messagebox.showwarning("No item selected", "Select an item from the list first.")
            return None
        product = self.inventory_service.product_repository.find_by_sku(self.selected_sku)
        if product is None:
            messagebox.showwarning("Item not found", "That item is no longer available.")
            self.refresh()
        return product

    def open_add_window(self):
        ProductDialog(self, "Add Item", self.add_product)

    def open_edit_window(self):
        product = self._selected_product()
        if product is None:
            return
        ProductDialog(self, "Edit Item", lambda values: self.update_product(product.sku, values), product)

    def open_sale_window(self):
        product = self._selected_product()
        if product is None:
            return
        SaleDialog(self, product, lambda amount: self.record_sale(product.sku, amount))

    def open_delete_window(self):
        product = self._selected_product()
        if product is None:
            return
        DeleteDialog(self, product, lambda: self.delete_product(product.sku))

    def add_product(self, values):
        try:
            self.inventory_service.add_product(values)
            self.refresh()
            return True
        except DuplicateKeyError:
            messagebox.showerror("Duplicate item", "This item already exists.")
        except Exception as exc:
            messagebox.showerror("Could not add item", str(exc))
        return False

    def update_product(self, sku, values):
        try:
            self.inventory_service.update_product(sku, values)
            self.refresh()
            self._select_product(sku)
            return True
        except Exception as exc:
            messagebox.showerror("Could not update item", str(exc))
        return False

    def delete_product(self, sku):
        self.inventory_service.delete_product(sku)
        self.selected_sku = None
        self.refresh()
        return True

    def record_sale(self, sku, amount):
        try:
            self.inventory_service.record_sale(sku, amount)
            self.refresh()
            self._select_product(sku)
            return True
        except Exception as exc:
            messagebox.showerror("Could not record sale", str(exc))
        return False

    def _select_product(self, sku):
        if sku in self.tree.get_children():
            self.tree.selection_set(sku)
            self.tree.focus(sku)
            self.selected_sku = sku
