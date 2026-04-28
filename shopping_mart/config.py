import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    mongo_uri: str = os.getenv("SHOPPING_MART_MONGO_URI", "mongodb://localhost:27017")
    database_name: str = os.getenv("SHOPPING_MART_DB", "shopping_mart_db")
    app_title: str = "Shopping Mart Product Management System"
