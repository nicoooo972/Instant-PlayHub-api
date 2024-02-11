# fake_data.py

from pymongo import MongoClient
from faker import Faker
import uuid
from passlib.hash import pbkdf2_sha256

# Connexion à la base de données MongoDB
client = MongoClient("localhost", 27017)
db = client.instantplayhub

# Génération de données fictives avec Faker
fake = Faker()

# Fonction pour générer un utilisateur fictif
def generate_fake_user():
    return {
        "_id": uuid.uuid4().hex,
        "username": fake.user_name(),
        "email": fake.email(),
        "password": pbkdf2_sha256.hash(fake.password()),  # Génération d'un mot de passe hashé avec Passlib
    }

# Fonction pour insérer des utilisateurs fictifs dans la base de données
def insert_fake_users(num_users):
    fake_users = [generate_fake_user() for _ in range(num_users)]
    db.users.insert_many(fake_users)

# Appel de la fonction pour insérer 10 utilisateurs fictifs
insert_fake_users(10)
