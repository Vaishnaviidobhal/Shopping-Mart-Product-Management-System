import tkinter as tk
from tkinter import messagebox, ttk

from pymongo.errors import DuplicateKeyError

from ui import styles


PRODUCT_FIELDS = [
    ("name", "Item Name"),
    ("category", "Category"),
    ("quantity", "Quantity"),
    ("price", "Price"),
    ("aisle", "Aisle"),
    ("shelf", "Shelf"),
]
STATS = [
    ("total", "Total Items", styles.PRIMARY),
    ("low_stock", "Low Stock", styles.WARNING),
    ("sold_out", "Sold Out", styles.DANGER),
    ("high_demand", "High Demand", styles.SUCCESS),
]
FILTERS = [
    ("All", "all", styles.PRIMARY),
    ("Low Stock", "low_stock", styles.WARNING),
    ("Sold Out", "sold_out", styles.DANGER),
    ("High Demand", "high_demand", styles.SUCCESS),
]
TABLE_COLUMNS = [
    ("name", "Item", 250),
    ("category", "Category", 130),
    ("quantity", "Available", 90),
    ("price", "Price", 90),
    ("location", "Location", 150),
    ("status", "Status", 120),
    ("sold_count", "Sold", 80),
]


def label(parent, text, **options):
    options.setdefault("font", styles.FONT)
    options.setdefault("bg", parent["bg"])
    return tk.Label(parent, text=text, **options)


def button(parent, text, color=None, **options):
    options.setdefault("font", styles.FONT)
    if color:
        options.update(bg=color, fg="white", activebackground=color, activeforeground="white")
    return tk.Button(parent, text=text, **options)


class BaseDialog(tk.Toplevel):
    def __init__(self, master, title, bg, accent):
        super().__init__(master)
        self.title(title)
        self.configure(bg=bg)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.shell = tk.Frame(self, bg=bg, padx=24, pady=20)
        self.shell.pack(fill="both", expand=True)
        label(self.shell, title, font=styles.TITLE_FONT, fg=accent).pack(anchor="w")


class ProductDialog(BaseDialog):
    def __init__(self, master, title, on_submit, product=None):
        super().__init__(master, title, styles.INPUT_PANEL, styles.ACCENT)
        self.on_submit = on_submit
        self.entries = {}
        self._build_form()
        self._fill(product)
        self.entries["name"].focus_set()

    def _build_form(self):
        form = tk.Frame(self.shell, bg=styles.INPUT_PANEL)
        form.pack(fill="x", pady=(14, 10))
        for key, text in PRODUCT_FIELDS:
            label(form, text).pack(anchor="w")
            self.entries[key] = tk.Entry(form, font=styles.FONT, width=36)
            self.entries[key].pack(fill="x", pady=(3, 9))

        row = tk.Frame(self.shell, bg=styles.INPUT_PANEL)
        row.pack(fill="x", pady=(6, 0))
        button(row, "Save", styles.SUCCESS, command=self._submit).pack(side="left", fill="x", expand=True)
        button(row, "Cancel", styles.WARNING, command=self.destroy).pack(
            side="left", fill="x", expand=True, padx=(10, 0)
        )

    def _fill(self, product):
        if not product:
            return
        values = {
            "name": product.name,
            "category": product.category,
            "quantity": product.quantity,
            "price": f"{product.price:.2f}",
            "aisle": product.aisle,
            "shelf": product.shelf,
        }
        for key, value in values.items():
            self.entries[key].insert(0, str(value))

    def _submit(self):
        if self.on_submit({key: entry.get() for key, entry in self.entries.items()}):
            self.destroy()


class SaleDialog(BaseDialog):
    def __init__(self, master, product, on_submit):
        super().__init__(master, "Record Sale", styles.OUTPUT_PANEL, styles.TEAL)
        self.on_submit = on_submit

        label(self.shell, f"{product.name} - Available: {product.quantity}", fg=styles.MUTED).pack(
            anchor="w", pady=(4, 14)
        )
        label(self.shell, "Quantity Sold").pack(anchor="w")
        self.amount_entry = tk.Entry(self.shell, font=styles.FONT, width=20)
        self.amount_entry.insert(0, "1")
        self.amount_entry.pack(fill="x", pady=(3, 14))
        self.amount_entry.focus_set()
        button(self.shell, "Record", styles.TEAL, command=self._submit).pack(fill="x")

    def _submit(self):
        if self.on_submit(self.amount_entry.get()):
            self.destroy()


class DashboardWindow(tk.Toplevel):
    COLUMNS = [column for column, _heading, _width in TABLE_COLUMNS]

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
        tree_style = ttk.Style(self)
        tree_style.theme_use("clam")
        tree_style.configure(
            "Treeview",
            font=styles.FONT,
            rowheight=30,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=styles.TEXT,
        )
        tree_style.configure(
            "Treeview.Heading",
            font=styles.SUBTITLE_FONT,
            background=styles.PRIMARY,
            foreground="white",
        )
        tree_style.map("Treeview", background=[("selected", styles.TEAL)])

    def _build(self):
        self._build_header()
        self._build_stats()
        body = tk.Frame(self, bg=styles.OUTPUT_PANEL, padx=18, pady=16)
        body.pack(fill="both", expand=True, padx=18, pady=14)
        self._build_actions(body)
        self._build_filters(body)
        self._build_table(body)

    def _build_header(self):
        header = tk.Frame(self, bg=styles.BG, padx=18, pady=14)
        header.pack(fill="x")
        title_box = tk.Frame(header, bg=styles.BG)
        title_box.pack(side="left")
        label(title_box, "Available Items", font=styles.TITLE_FONT, fg=styles.PURPLE).pack(anchor="w")
        label(title_box, "Select an item, then choose what you want to do", fg=styles.MUTED).pack(anchor="w")
        label(header, f"Signed in as {self.employee.full_name}", fg=styles.MUTED).pack(side="right")

    def _build_stats(self):
        stats = tk.Frame(self, bg=styles.BG, padx=18)
        stats.pack(fill="x")
        self.stat_labels = {}

        for key, title, color in STATS:
            card = tk.Frame(
                stats,
                bg=styles.PANEL,
                padx=14,
                pady=10,
                highlightbackground=color,
                highlightthickness=2,
            )
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            label(card, title, fg=styles.MUTED).pack(anchor="w")
            self.stat_labels[key] = label(card, "0", font=("Segoe UI", 18, "bold"), fg=color)
            self.stat_labels[key].pack(anchor="w")

    def _build_actions(self, parent):
        bar = tk.Frame(parent, bg=styles.OUTPUT_PANEL)
        bar.pack(fill="x", pady=(0, 12))
        actions = [
            ("Add Item", styles.SUCCESS, self.open_add_window),
            ("Edit Selected", styles.PRIMARY, self.open_edit_window),
            ("Record Sale", styles.TEAL, self.open_sale_window),
            ("Delete Selected", styles.DANGER, self.open_delete_window),
        ]
        for text, color, command in actions:
            button(bar, text, color, command=command).pack(side="left", padx=(0, 8))

        button(bar, "Refresh", styles.WARNING, command=self.refresh).pack(side="right")
        search_entry = tk.Entry(bar, textvariable=self.search_text, font=styles.FONT, width=26)
        search_entry.pack(side="right", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh())
        label(bar, "Search").pack(side="right", padx=(0, 6))

    def _build_filters(self, parent):
        bar = tk.Frame(parent, bg=styles.OUTPUT_PANEL)
        bar.pack(fill="x", pady=(0, 12))
        for text, value, color in FILTERS:
            button(bar, text, color, command=lambda selected=value: self.set_filter(selected)).pack(
                side="left", padx=(0, 8)
            )

    def _build_table(self, parent):
        self.tree = ttk.Treeview(parent, columns=self.COLUMNS, show="headings", selectmode="browse")
        for column, heading, width in TABLE_COLUMNS:
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="w")

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
        for key, value in self.inventory_service.dashboard_counts().items():
            self.stat_labels[key].configure(text=str(value))

        self.tree.delete(*self.tree.get_children())
        for product in self._filtered_products():
            status = self.inventory_service.stock_status(product)
            self.tree.insert("", "end", iid=product.sku, values=self._row_values(product, status), tags=(self._tag(status),))

        if self.selected_sku not in self.tree.get_children():
            self.selected_sku = None

    def _filtered_products(self):
        getters = {
            "all": self.inventory_service.all_products,
            "low_stock": self.inventory_service.low_stock_products,
            "sold_out": self.inventory_service.sold_out_products,
            "high_demand": self.inventory_service.high_demand_products,
        }
        products = getters[self.current_filter]()
        query = self.search_text.get().lower().strip()
        return [product for product in products if self._matches(product, query)] if query else products

    def _matches(self, product, query):
        return any(
            query in value.lower()
            for value in (product.name, product.category, product.get_location())
        )

    def _row_values(self, product, status):
        return (
            product.name,
            product.category,
            product.quantity,
            f"{product.price:.2f}",
            product.get_location(),
            status,
            product.sold_count,
        )

    def _tag(self, status):
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
        if product:
            ProductDialog(self, "Edit Item", lambda values: self.update_product(product.sku, values), product)

    def open_sale_window(self):
        product = self._selected_product()
        if product:
            SaleDialog(self, product, lambda amount: self.record_sale(product.sku, amount))

    def open_delete_window(self):
        product = self._selected_product()
        if product and messagebox.askyesno("Delete Item", f"Remove {product.name} from the mart list?"):
            self.delete_product(product.sku)

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
