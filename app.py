# app.py

import os
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from gevent import pywsgi
from app.infrastructure.user import User
from app.infrastructure.chat import Chat
from app.infrastructure.chat import Message
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.middlewares.authMiddleware import AuthMiddleware
from dotenv import load_dotenv
from app.morpion.infrastructure.socket_manager import setup_morpion_sockets
from geventwebsocket.handler import WebSocketHandler
from flask_jwt_extended import jwt_required

app = Flask(__name__, template_folder='templates')
app.debug = True
CORS(app)

# Initialisation du middleware
auth_middleware = AuthMiddleware(app)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de la clé secrète pour les tokens JWT
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# ---------- Setup ----------
setup_morpion_sockets(socketio)


# ---------- Utilisateur ----------

@app.route('/')
def home():
    return "Page d'accueil de l'application Flask !"


@app.route('/games/uno')
def getGamesUno():
    return [];


# Création de compte utilisateur
@app.route('/register', methods=['POST'])
def register():
    user = User()
    return user.register()


# Connexion compte utilisateur
@app.route('/login', methods=['POST'])
def login():
    user = User()
    return user.login()


# Récupérer les informations de l'utilisateur connecté
@app.route('/user/info', methods=['GET'])
@jwt_required()
def get_user_info():
    user = User()
    return user.get_user_info()


# Modifier les informations de l'utilisateur connecté
@app.route('/user/update', methods=['PUT'])
@jwt_required()
def update_user_info():
    user = User()
    return user.update_user_info()


# Supprimer son compte
@app.route('/user/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    user = User()
    return user.delete_account()


# Récupérer les informations de tous les utilisateurs
@app.route('/users', methods=['GET'])
def get_all_users():
    user = User()
    return user.get_all_users()


# Récupérer les informations d'un utilisateur
@app.route('/user/<userId>', methods=['GET'])
@jwt_required()
def get_one_user(userId):
    print(userId)
    user = User()
    return user.get_one_user(userId)


# Ajouter un autre utilisateur comme ami
@app.route('/user/<user_id>/add_friend', methods=['POST'])
@jwt_required()
def add_friend(user_id):
    user = User()
    return user.add_friend(user_id)


# Récupérer la liste d'amis (de l'utilisateur connecté)
@app.route('/user/friends-list', methods=['GET'])
@jwt_required()
def get_friends():
    user = User()
    return user.get_friends()


@app.route('/user/chats', methods=['GET'])
@jwt_required()
def get_user_chats():
    user = User()
    return user.get_user_chats()


# Déconnexion compte utilisateur
@app.route('/logout', methods=['POST'])
def logout():
    user = User()
    return user.logout()


# ---------- Morpion ----------

@app.route('/morpion')
def morpion():
    return render_template('morpion.html')


@app.route('/morpion/rooms')
def rooms():
    return render_template('rooms.html')


# ---------- Chat ----------
@app.route('/chat/check_or_create/<friend_id>', methods=['POST'])
@jwt_required()
def check_or_create_chat(friend_id):
    chat_service = Chat()
    return chat_service.check_or_create_chat(friend_id)


# Créer un chat
@app.route('/chat/create', methods=['POST'])
@jwt_required()
def create_chat():
    chat_data = request.json
    # Extraction des données de la requête
    users = chat_data.get('Users')

    if not users:
        return jsonify({"error": "Liste d'utilisateurs requise."}), 400

    # Créer le chat
    chat = Chat()
    chat_id = chat.create_chat(chat_data)

    # On retourne le chat ID
    return jsonify({"chat_id": chat_id}), 200


# Récupérer un chat
@app.route('/chat/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    chat = Chat()
    return chat.get_one_chat(chat_id)


# Ajouter un utilisateur à un chat
@app.route('/chat/add_users/<chat_id>', methods=['POST'])
@auth_middleware.require_authentication
def add_users_to_chat(chat_id):
    users_data = request.json
    users = users_data.get('users', [])
    chat_service = Chat()
    chat_service.add_users_to_chat(chat_id, users)
    return jsonify({"message": "Utilisateur ajouté au chat avec succès."}), 200


# Récupérer la liste des chats (de l'utilisateur connecté)
@app.route('/chat/chats-list', methods=['GET'])
@jwt_required()
def get_chats():
    chat = Chat()
    return chat.get_chats()


# Récupérer les messages d'un chat
@app.route('/chat/messages/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat_messages(chat_id):
    chat_service = Chat()
    messages = chat_service.get_chat_messages(chat_id)
    return jsonify({"messages": messages}), 200


# Envoyer un message dans un chat
@app.route('/chat/send_message', methods=['POST'])
@jwt_required()
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    user_id = data.get('user_id')
    message = data.get('message')

    chat_service = Chat()
    chat_service.send_message(chat_id, user_id, message)

    return jsonify({"message": "Message envoyé avec succès"}), 200


# Supprimer un chat (supprime le chat uniquement pour l'utilisateur qui fait
# la requête)
@app.route('/chat/delete/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    chat = Chat()
    return chat.delete_chat(chat_id)


# ========================= SOCKETS =========================

@socketio.on('connect')
def connect():
    print(f'Le client {request.sid} est connecté')


@socketio.on('disconnect')
def disconnect():
    emit('disconnect')
    print(f'Le client {request.sid} est déconnecté')


@socketio.on('join')
def on_join(data):
    chat_id = data['chat_id']
    join_room(chat_id)
    print(f'Le client {request.sid} a rejoint la salle {chat_id}')


@socketio.on('leave')
def on_leave(data):
    chat_id = data['chat_id']
    leave_room(chat_id)
    print(f'Le client {request.sid} a quitté la salle {chat_id}')


@socketio.on('message')
def handle_message(data):
    chat_id = data['chat_id']
    user_id = data['user_id']
    message = data['message']

    chat_service = Chat()
    chat_service.send_message(chat_id, {
        "user_id": user_id,
        "message": message
    })

    socketio.emit('message', {
        "chat_id": chat_id,
        "user_id": user_id,
        "message": message
    }, room=chat_id)


if __name__ == '__main__':
    app.logger.setLevel(logging.ERROR)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    app.logger.addHandler(stream_handler)
    socketio.run(app, host='0.0.0.0', port=5000)
