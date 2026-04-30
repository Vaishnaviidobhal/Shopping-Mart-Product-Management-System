import tkinter as tk
from tkinter import messagebox

from ui import styles


class LoginWindow(tk.Toplevel):
    def __init__(self, master, auth_service, on_success):
        super().__init__(master)
        self.auth_service = auth_service
        self.on_success = on_success

        self.title("Shopping Mart Employee Access")
        self.state("zoomed")
        self.configure(bg=styles.BG)
        self.protocol("WM_DELETE_WINDOW", self._close_app)
        self.bind("<Escape>", lambda _event: self.state("normal"))

        self._build()
        self.login_username_entry.focus_set()

    def _build(self):
        shell = tk.Frame(self, bg=styles.BG, padx=40, pady=34)
        shell.pack(expand=True, fill="both")

        tk.Label(
            shell,
            text="Shopping Mart",
            font=("Segoe UI", 24, "bold"),
            bg=styles.BG,
            fg=styles.TEXT,
        ).pack(anchor="w")
        tk.Label(
            shell,
            text="Permanent employee key only",
            font=styles.FONT,
            bg=styles.BG,
            fg=styles.MUTED,
        ).pack(anchor="w", pady=(2, 26))

        panels = tk.Frame(shell, bg=styles.BG)
        panels.pack(expand=True)

        login_panel = tk.Frame(
            panels,
            bg=styles.OUTPUT_PANEL,
            padx=42,
            pady=36,
            highlightbackground=styles.PRIMARY,
            highlightthickness=2,
        )
        login_panel.pack(fill="both")
        self._build_login_panel(login_panel)

        tk.Label(
            shell,
            text="Press Esc to leave full-screen mode",
            font=("Segoe UI", 9),
            bg=styles.BG,
            fg=styles.MUTED,
        ).pack(anchor="e", pady=(12, 0))

    def _build_login_panel(self, panel):
        tk.Label(
            panel,
            text="Login",
            font=styles.TITLE_FONT,
            bg=styles.OUTPUT_PANEL,
            fg=styles.TEXT,
        ).pack(anchor="w")
        tk.Label(
            panel,
            text="Use the fixed admin key",
            font=styles.FONT,
            bg=styles.OUTPUT_PANEL,
            fg=styles.MUTED,
        ).pack(anchor="w", pady=(2, 24))

        tk.Label(panel, text="Username", font=styles.FONT, bg=styles.OUTPUT_PANEL).pack(anchor="w")
        self.login_username_entry = tk.Entry(panel, font=styles.FONT)
        self.login_username_entry.insert(0, "admin")
        self.login_username_entry.pack(fill="x", pady=(4, 14))

        tk.Label(panel, text="Password", font=styles.FONT, bg=styles.OUTPUT_PANEL).pack(anchor="w")
        self.login_password_entry = tk.Entry(panel, font=styles.FONT, show="*")
        self.login_password_entry.pack(fill="x", pady=(4, 22))
        self.login_password_entry.bind("<Return>", lambda _event: self._login())

        tk.Button(
            panel,
            text="Login",
            font=styles.FONT,
            bg=styles.PRIMARY,
            fg="white",
            activebackground=styles.PRIMARY,
            activeforeground="white",
            command=self._login,
        ).pack(fill="x", ipady=5)

        tk.Label(
            panel,
            text="Username: admin    Password: admin123",
            font=("Segoe UI", 9),
            bg=styles.OUTPUT_PANEL,
            fg=styles.MUTED,
        ).pack(anchor="w", pady=(16, 0))

    def _login(self):
        employee = self.auth_service.login(
            self.login_username_entry.get(),
            self.login_password_entry.get(),
        )
        if employee is None:
            messagebox.showerror("Login failed", "Invalid username or password.")
            return

        self.destroy()
        self.on_success(employee)

    def _close_app(self):
        self.master.destroy()
