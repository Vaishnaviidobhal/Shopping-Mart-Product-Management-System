from shopping_mart.models.employee import Employee


class EmployeeRepository:
    def __init__(self, collection):
        self.collection = collection

    def count(self):
        return self.collection.count_documents({})

    def find_by_username(self, username):
        document = self.collection.find_one({"username": username.lower().strip()})
        return Employee.from_document(document) if document else None

    def create(self, employee):
        self.collection.insert_one(employee.to_document())

    def upsert(self, employee):
        self.collection.update_one(
            {"username": employee.username.lower().strip()},
            {"$set": employee.to_document()},
            upsert=True,
        )
