from shopping_mart.models.employee import Employee
from shopping_mart.utils.security import hash_password


class AuthService:
    PERMANENT_USERNAME = "navi"
    PERMANENT_PASSWORD = "123navi"
    PERMANENT_FULL_NAME = "Navi"
    PERMANENT_ROLE = "manager"

    def __init__(self, employee_repository):
        self.employee_repository = employee_repository

    def register_employee(self, username, password, full_name, role="employee"):
        username = username.lower().strip()
        full_name = full_name.strip()
        self._validate_signup(username, password, full_name)

        employee = Employee(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
        )
        self.employee_repository.create(employee)
        return employee

    def login(self, username, password):
        username = username.lower().strip()
        if username != self.PERMANENT_USERNAME:
            return None
        if password != self.PERMANENT_PASSWORD:
            return None

        employee = self.employee_repository.find_by_username(username)
        if employee is None:
            return Employee(
                username=self.PERMANENT_USERNAME,
                password_hash=hash_password(self.PERMANENT_PASSWORD),
                full_name=self.PERMANENT_FULL_NAME,
                role=self.PERMANENT_ROLE,
            )
        return employee

    def has_employees(self):
        return self.employee_repository.count() > 0

    def _validate_signup(self, username, password, full_name):
        if not full_name:
            raise ValueError("Full name is required.")
        if not username:
            raise ValueError("Username is required.")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
