# app/infrastructure/user.py

from flask import jsonify, request
import uuid
import os
from passlib.hash import pbkdf2_sha256
from db import db
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

# Modèle d'utilisateur
class User:
    # Création compte utilisateur
    def register(self):
        user_data = request.json

        user = {
            "_id": uuid.uuid4().hex,
            "username": user_data.get('username'),
            "email": user_data.get('email'),
            "password": user_data.get('password'),
        }

        if secret_key is None:
            return jsonify({"error": "La clé secrète n'est pas définie !"}), 500

        try:
            secret_key_bytes = secret_key.encode('utf-8')
        except Exception as e:
            return jsonify({"error": "Erreur lors de l'encodage de la clé secrète en bytes !", "details": str(e)}), 500

        user["password"] = pbkdf2_sha256.hash(user['password'], salt=secret_key_bytes)

        if db.users.find_one({"email": user["email"]}):
            return jsonify({"error": "Cette adresse Email est déjà utilisée par un utilisateur !"}), 400
  
        if db.users.insert_one(user):
            return jsonify(user), 200

        return jsonify({"error": "L'inscription a échouée."}), 400
    
    # Connexion compte utilisateur
    def login(self):
        login_data = request.json
        email = login_data.get('email')
        password = login_data.get('password')

        user = db.users.find_one({"email": email})
        if user and pbkdf2_sha256.verify(password, user['password']):
            return jsonify({"message": "Connexion réussie !"}), 200
        else:
            return jsonify({"error": "Adresse Email ou mot de passe incorrect !"}), 401
    
    # Déconnexion compte utilisateur
    def logout(self):
        return jsonify({"message": "Déconnexion réussie !"}), 200

  
user = User()