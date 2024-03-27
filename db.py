# db.py

# from pymongo import MongoClient

# class Database:
#     def __init__(self, uri, db_name):
#         self.client = MongoClient(uri)
#         self.db = self.client[db_name]
#         self.users_collection = self.db['users']

# Configurez votre URI et le nom de la base de données
# DATABASE_URI = 'mongodb://localhost:27017/'
# DATABASE_NAME = 'instantplayhub'

# Initialisez une instance de la classe Database pour être utilisée ailleurs dans votre application
# db = Database(DATABASE_URI, DATABASE_NAME)

import pymongo

client = pymongo.MongoClient("localhost", 27017)
db = client.instantplayhub