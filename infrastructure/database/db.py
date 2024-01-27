# infrastructure/database/db.py
from pymongo import MongoClient

class MongoDB:
    def __init__(self, db_url, db_name):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]
