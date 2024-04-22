# app/infrastructure/chat.py

from db import db
from datetime import datetime
import uuid


# from flask import jsonify, request


# Modèle d'un chat
class Chat:
    def send_message(self, chat_id, message_data):
        message_id = uuid.uuid4().hex  # Générer un ID unique pour le message
        message_data[
            "_id"] = message_id  # Ajouter l'ID du message aux données du
        # message

        # Enregistrer le message dans la collection "message"
        db.message.insert_one(message_data)

        # Mettre à jour le champ "Messages" du document du chat
        # correspondant dans la collection "chat"
        db.chat.update_one({"_id": chat_id},
                           {"$addToSet": {"Messages": message_id}})

    def get_messages(self):
        messages = list(
            db.message.find())  # Récupérer l'historique des messages depuis
        # la base de
        # données MongoDB
        return messages

    def create_chat(self, name, users):
        now = datetime.now()  # Date de création du chat
        created_at = now.strftime(
            "%d/%m/%Y %H:%M:%S")  # Formatage de la date -> dd/mm/YY H:M:S

        chat_data = {
            "_id": uuid.uuid4().hex,
            "name": name,
            "Users": users,
            "Messages": [],
            "created_at": created_at
        }
        db.chat.insert_one(chat_data)

    # Méthode pour ajouter des utilisateurs à un chat existant
    def add_users_to_chat(self, chat_id, users):
        db.chat.update_one({"_id": chat_id},
                           {"$addToSet": {"users": {"$each": users}}})

    # Méthode pour récupérer les messages d'un chat spécifique
    def get_chat_messages(self, chat_id):
        chat = db.chat.find_one({"_id": chat_id})
        if chat:
            return chat["messages"]
        else:
            return []
