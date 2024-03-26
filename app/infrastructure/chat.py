# app/infrastructure/chat.py

from db import db
from datetime import datetime
import uuid
from flask import jsonify, request



class Chat:
    def send_message(self, message_data):
        # Enregistrer le message dans la base de données MongoDB
        db.messages.insert_one(message_data)

    def get_messages(self):
        # Récupérer l'historique des messages depuis la base de données MongoDB
        messages = list(db.messages.find())
        return messages

    def create_chat(self, name, users):
        # Date de création du chat
        now = datetime.now()
        # Formatage de la date -> dd/mm/YY H:M:S
        created_at = now.strftime("%d/%m/%Y %H:%M:%S")
        
        chat_data = {
            "_id": uuid.uuid4().hex,
            "name": name,
            "users": users,
            "messages": [],
            "created_at": created_at
        }
        db.chat.insert_one(chat_data)

    # Méthode pour ajouter des utilisateurs à un chat existant
    def add_users_to_chat(self, chat_id, users):
        db.chat.update_one({"_id": chat_id}, {"$addToSet": {"users": {"$each": users}}})

    # Méthode pour récupérer les messages d'un chat spécifique
    def get_chat_messages(self, chat_id):
        chat = db.chat.find_one({"_id": chat_id})
        if chat:
            return chat["messages"]
        else:
            return []