# app/infrastructure/user.py

import logging
from flask import jsonify, request
import uuid
import os
from passlib.hash import pbkdf2_sha256
from db import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

# Modèle d'utilisateur
class User:
    # Création compte utilisateur
    def register(self):
        user_data = request.json
        
        # Date de création de l'utilisateur
        now = datetime.now()
        # Formatage de la date -> dd/mm/YY H:M:S
        created_at = now.strftime("%d/%m/%Y %H:%M:%S")

        user = {
            "_id": uuid.uuid4().hex,
            "username": user_data.get('username'),
            "email": user_data.get('email'),
            "password": user_data.get('password'),
            "created_at": created_at
        }

        if secret_key is None:
            return jsonify({"error": "La clé secrète n'est pas définie !"}), 500

        try:
            secret_key_bytes = secret_key.encode('utf-8')
        except Exception as e:
            return jsonify({"error": "Erreur lors de l'encodage de la clé secrète en bytes !", "details": str(e)}), 500

        user["password"] = pbkdf2_sha256.hash(user['password'], salt=secret_key_bytes)

        if db.user.find_one({"email": user["email"]}):
            return jsonify({"error": "Cette adresse Email est déjà utilisée par un utilisateur !"}), 400
  
        if db.user.insert_one(user):
            return jsonify(user), 200

        return jsonify({"error": "L'inscription a échouée."}), 400
    
    # Connexion compte utilisateur
    def login(self):
        login_data = request.json
        email = login_data.get('email')
        password = login_data.get('password')
        
        user = db.user.find_one({"email": email})
        if user and pbkdf2_sha256.verify(password, user['password']):
            access_token = create_access_token(identity=email, expires_delta=timedelta(hours=24))  # Création du token JWT avec l'email de l'utilisateur
            logging.info(f"Connexion réussie pour l'utilisateur avec l'email {email}.")
            return jsonify({"message": "Vous êtes connecté ! ", "Token de connexion : ": access_token}), 200  # Retourner le token dans la réponse JSON
        else:
            logging.error("Tentative de connexion échouée.")
            return jsonify({"error": "Adresse Email ou mot de passe incorrect !"}), 401
    
    # Déconnexion compte utilisateur avec expiration du token JWT
    @jwt_required()
    def logout(self):
        unset_jwt_cookies()  # Expiration du token JWT
        return jsonify({"message": "Vous êtes déconnecté."}), 200

  
user = User()