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
        
    @jwt_required()
    def check_or_create_chat(self, friend_id):
        current_user_email = get_jwt_identity()
        current_user = db.user.find_one({"email": current_user_email})

        if not current_user:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        # Rechercher un chat existant entre les deux utilisateurs
        existing_chat = db.chat.find_one({
            "Users": {"$all": [current_user["_id"], friend_id]},
            "isGroup": False
        })

        if existing_chat:
            return jsonify({
                "message": "Chat existant.",
                "chat_id": existing_chat["_id"]
            }), 200

        # Si le chat n'existe pas, créer un nouveau chat
        now = datetime.now()
        created_at = now.strftime("%d/%m/%Y %H:%M:%S")
        new_chat = {
            "_id": uuid.uuid4().hex,
            "name": "Chat",
            "Users": [current_user["_id"], friend_id],
            "Messages": [],
            "isGroup": False,
            "created_at": created_at
        }

        if db.chat.insert_one(new_chat):
            new_chat_id = new_chat["_id"]
            # Mettre à jour l'utilisateur actuel avec le nouvel ID de chat
            db.user.update_one(
                {"_id": current_user["_id"]},
                {"$push": {"Chats": new_chat_id}}
            )
            # Mettre à jour l'ami avec le nouvel ID de chat
            db.user.update_one(
                {"_id": friend_id},
                {"$push": {"Chats": new_chat_id}}
            )
            return jsonify({
                "message": "Nouveau chat créé.",
                "chat_id": new_chat_id
            }), 201

        return jsonify({"error": "Échec de la création du chat."}), 500

    # Créer un chat
    def create_chat(self, chat_data):
        
        current_user_email = get_jwt_identity()
        current_user = db.user.find_one({"email": current_user_email})
        now = datetime.now()  # Date de création du chat
        created_at = now.strftime(
            "%d/%m/%Y %H:%M:%S")  # Formatage de la date -> dd/mm/YY H:M:S

        chat = {
            "_id": uuid.uuid4().hex,
            "name": chat_data.get('name'),
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
        
    # Méthode pour récupérer les chats d'un utilisateur
    @jwt_required()
    def get_user_chats(self):
        current_user_email = get_jwt_identity()
        current_user = db.user.find_one({"email": current_user_email})
        if not current_user:
            return jsonify({"error": "Utilisateur non trouvé."}), 404

        user_chats = []
        for chat_id in current_user.get("Chats", []):
            chat = db.chat.find_one({"_id": chat_id})
            if chat:
                other_user_id = [user_id for user_id in chat["Users"] if user_id != current_user["_id"]][0]
                other_user = db.user.find_one({"_id": other_user_id}, {"username": 1, "profile_picture": 1})
                if other_user:
                    user_chats.append({
                        "chat_id": chat["_id"],
                        "other_user": other_user,
                        "created_at": chat["created_at"]
                    })

        return jsonify({"chats": user_chats}), 200

