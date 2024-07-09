# app/infrastructure/chat.py

from flask import jsonify
from db import db
from datetime import datetime
import uuid
from flask_jwt_extended import create_access_token, jwt_required, \
    get_jwt_identity, \
    unset_jwt_cookies
from dotenv import load_dotenv
from app.infrastructure.message import Message
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
    def send_message(self, chat_id, user_id, message):
        new_message = Message(chat_id, user_id, message)
        new_message.save_to_db()

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
        messages = Message.get_messages_by_chat_id(chat_id)
        return messages

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
