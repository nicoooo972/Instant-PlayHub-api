# app/infrastructure/chat.py

from flask import jsonify
from db import db
from datetime import datetime
import uuid
from flask_jwt_extended import create_access_token, jwt_required, \
    get_jwt_identity, \
    unset_jwt_cookies
from dotenv import load_dotenv
load_dotenv()

# Class d'un chat
class Chat:

    # Créer un chat
    def create_chat(self, chat_data):
        
        current_user_email = get_jwt_identity()
        current_user = db.user.find_one({"email": current_user_email})
        now = datetime.now()  # Date de création du chat
        created_at = now.strftime(
            "%d/%m/%Y %H:%M:%S")  # Formatage de la date -> dd/mm/YY H:M:S

        # Récupérer l'utilisateur avec qui on souhaite parler (autre que l'utilisateur actuel)
        other_user_id = [user_id for user_id in chat_data.get('Users') if user_id != current_user["_id"]][0]
        other_user = db.user.find_one({"_id": other_user_id})
        chat_name = other_user['username']  # Utiliser le username de l'autre utilisateur comme nom du chat

        chat = {
            "_id": uuid.uuid4().hex,
            "name": chat_name,
            "Users": chat_data.get('Users'),
            "Messages": [],
            "isGroup": len(chat_data.get('Users')) > 2,
            "created_at": created_at
        }
        
        if db.chat.insert_one(chat):
            chat_id = chat["_id"]
            for user_id in chat["Users"]:
                if user_id != current_user["_id"]:
                    db.user.update_one({"_id": user_id}, {"$push": {"Chats": chat_id}})

            current_user["Chats"] = current_user.get("Chats", []) + [chat_id]
            db.user.update_one({"email": current_user_email}, {"$set": {"Chats": current_user["Chats"]}})

            return chat, 201

        return jsonify({"error": "Échec de la création du chat."}), 500
    
    # Récupérer un chat
    @jwt_required()
    def get_one_chat(self, chat_id):
        current_user_email = get_jwt_identity()
        user = db.user.find_one({"email": current_user_email})
        if not user:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        chat = db.chat.find_one({"_id": chat_id})
        if chat and chat["_id"] in user["Chats"]:
            return jsonify(chat), 200 
        else:
            return jsonify({"error": "Accès non autorisé à ce chat."}), 403
    
    # Envoyer un message
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

    # Récupérer les chats (de l'utilisateur connecté)
    @jwt_required()
    def get_chats(self):
        current_user_email = get_jwt_identity()
        user = db.user.find_one({"email": current_user_email})
        if not user:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        # Récupérer la liste des chats
        chats_ids = user.get("Chats", [])

        # Récupérer les informations des chats
        chats = []
        for chat_id in chats_ids:
            chat = db.chat.find_one({"_id": chat_id})
            if chat:
                chats.append(chat)

        return jsonify({"Chats": chats}), 200

    # Récupérer les messages d'un chat
    def get_messages(self):
        messages = list(
            db.message.find())  # Récupérer l'historique des messages depuis
        # la base de
        # données MongoDB
        return messages

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

    # Supprimer un chat (le chat est supprimé pour tous les utilisateurs)
    @jwt_required()
    def delete_chat(self, chat_id):
        current_user_email = get_jwt_identity()
        user = db.user.find_one({"email": current_user_email})
        if not user:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        chat = db.chat.find_one({"_id": chat_id})
        if not chat:
            return jsonify({"error": "Chat non trouvé."}), 404

        # Supprimer le chat de la liste des chats de tous les utilisateurs concernés
        user_ids = chat.get("Users", [])
        for user_id in user_ids:
            db.user.update_one(
                {"_id": user_id},
                {"$pull": {"Chats": chat_id}}
            )

        # Supprimer le document du chat de la collection 'chat'
        db.chat.delete_one({"_id": chat_id})

        return jsonify({"message": "Chat supprimé avec succès."}), 200
