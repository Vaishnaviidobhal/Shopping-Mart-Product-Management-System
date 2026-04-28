from pymongo import MongoClient


class MongoDB:
    def __init__(self, config):
        self.client = MongoClient(config.mongo_uri, serverSelectionTimeoutMS=3000)
        self.database = self.client[config.database_name]
        self.employees = self.database["employees"]
        self.products = self.database["products"]

    def _create_indexes(self):
        self.employees.create_index("username", unique=True)
        self.products.create_index("sku", unique=True)
        self.products.create_index("quantity")
        self.products.create_index("reorder_level")

    def ping(self):
        self.client.admin.command("ping")
        self._create_indexes()
