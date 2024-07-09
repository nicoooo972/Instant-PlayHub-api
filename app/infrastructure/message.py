# app/infrastructure/message.py

from db import db
from datetime import datetime
import uuid

class Message:
    def __init__(self, chat_id, user_id, message):
        self._id = uuid.uuid4().hex
        self.chat_id = chat_id
        self.user_id = user_id
        self.message = message
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def save_to_db(self):
        message_data = {
            "_id": self._id,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp
        }
        db.message.insert_one(message_data)
        db.chat.update_one({"_id": self.chat_id}, {"$addToSet": {"Messages": self._id}})

    @staticmethod
    def get_messages_by_chat_id(chat_id):
        messages_ids = db.chat.find_one({"_id": chat_id}).get("Messages", [])
        messages = list(db.message.find({"_id": {"$in": messages_ids}}))
        return messages
