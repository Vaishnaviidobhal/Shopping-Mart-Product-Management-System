import hashlib

from models import Employee, employee_from_document


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class EmployeeRepository:
    def __init__(self, collection):
        self.collection = collection

    def count(self):
        return self.collection.count_documents({})

    def find_by_username(self, username):
        document = self.collection.find_one({"username": username.lower().strip()})
        return employee_from_document(document) if document else None

    def create(self, employee):
        self.collection.insert_one(employee.to_document())

    def upsert(self, employee):
        self.collection.update_one(
            {"username": employee.username.lower().strip()},
            {"$set": employee.to_document()},
            upsert=True,
        )


class AuthService:
    PERMANENT_USERNAME = "admin"
    PERMANENT_PASSWORD = "admin123"
    PERMANENT_FULL_NAME = "Admin"
    PERMANENT_ROLE = "admin"

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

    def ensure_default_employee(self):
        employee = Employee(
            username=self.PERMANENT_USERNAME,
            password_hash=hash_password(self.PERMANENT_PASSWORD),
            full_name=self.PERMANENT_FULL_NAME,
            role=self.PERMANENT_ROLE,
        )
        self.employee_repository.upsert(employee)

    def _validate_signup(self, username, password, full_name):
        if not full_name:
            raise ValueError("Full name is required.")
        if not username:
            raise ValueError("Username is required.")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
