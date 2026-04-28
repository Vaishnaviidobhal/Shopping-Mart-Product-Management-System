from dataclasses import dataclass


@dataclass
class Employee:
    username: str
    password_hash: str
    full_name: str
    role: str = "employee"

    def to_document(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "role": self.role,
        }

    @classmethod
    def from_document(cls, document):
        return cls(
            username=document["username"],
            password_hash=document["password_hash"],
            full_name=document.get("full_name", "Employee"),
            role=document.get("role", "employee"),
        )
