from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.user = self.db['users']


DATABASE_URI = os.getenv("DATABASE_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
CLIENT = os.getenv("CLIENT")

db = Database(DATABASE_URI, DATABASE_NAME)
client = MongoClient(DATABASE_URI)
db = client[CLIENT]
