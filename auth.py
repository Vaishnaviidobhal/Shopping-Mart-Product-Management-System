from models import Employee


class AuthService:
    USERNAME = "admin"
    PASSWORD = "admin123"

    def login(self, username, password):
        if username.lower().strip() == self.USERNAME and password == self.PASSWORD:
            return Employee(username=self.USERNAME, full_name="Admin", role="admin")
        return None
