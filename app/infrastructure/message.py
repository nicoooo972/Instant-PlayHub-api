# app/infrastructure/message.py

from flask import jsonify
from db import db
from datetime import datetime
import uuid
from flask_jwt_extended import create_access_token, jwt_required, \
    get_jwt_identity, \
    unset_jwt_cookies
from dotenv import load_dotenv
load_dotenv()

# Modèle d'un message
class Message:

    # Envoyer un message
    def send_message(self, chat_id, content):
        current_user_email = get_jwt_identity()
        sender = db.user.find_one({"email": current_user_email})
        chat = db.chat.find_one({"_id": chat_id})

        if not sender or not chat:
            return jsonify({"error": "Utilisateur ou chat non trouvé."}), 404

        receiver_id = [user_id for user_id in chat["Users"] if user_id != sender["_id"]][0]
        receiver = db.user.find_one({"_id": receiver_id})

        message_data = {
            "_id": uuid.uuid4().hex,
            "content": content,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Sender": sender["_id"],
            "Receiver": receiver["_id"],
            "Chat": chat_id
        }

        # Enregistrer le message dans la collection "message"
        db.message.insert_one(message_data)

        # Mettre à jour le champ "Messages" du document du chat
        db.chat.update_one({"_id": chat_id}, {"$addToSet": {"Messages": message_data["_id"]}})

        return jsonify({"message": "Message envoyé avec succès."}), 200

    # Supprimer un message
    @jwt_required()
    def delete_message(self, message_id):
        current_user_email = get_jwt_identity()
        current_user = db.user.find_one({"email": current_user_email})
        
        message = db.message.find_one({"_id": message_id})

        if not message:
            return jsonify({"error": "Message non trouvé."}), 404
        
        if message["Sender"] != current_user["_id"]:
            return jsonify({"error": "Non autorisé à supprimer ce message."}), 403

        db.message.delete_one({"_id": message_id})
        db.chat.update_one({"_id": message["Chat"]}, {"$pull": {"Messages": message_id}})
        
        return jsonify({"message": "Message supprimé avec succès."}), 200

    # Modifier un message
    @jwt_required()
    def edit_message(self, message_id, new_content):
        current_user_email = get_jwt_identity()
        current_user = db.user.find_one({"email": current_user_email})
        
        message = db.message.find_one({"_id": message_id})

        if not message:
            return jsonify({"error": "Message non trouvé."}), 404
        
        if message["Sender"] != current_user["_id"]:
            return jsonify({"error": "Non autorisé à modifier ce message."}), 403

        db.message.update_one({"_id": message_id}, {"$set": {"content": new_content, "edited_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}})
        
        return jsonify({"message": "Message modifié avec succès."}), 200

    # Récupérer tous les messages de la plateforme
    def get_messages(self):
        messages = list(
            db.message.find())  # Récupérer l'historique des messages depuis la base de données MongoDB
        return messages
    
    def get_messages_by_chat_id(chat_id):
        messages_ids = db.chat.find_one({"_id": chat_id}).get("Messages", [])
        messages = list(db.message.find({"_id": {"$in": messages_ids}}).sort("created_at", 1))  # Sort by timestamp descending
        return messages

message = Message()
