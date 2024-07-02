# app.py

import os
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from gevent import pywsgi
from app.infrastructure.user import User
from app.infrastructure.chat import Chat
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from app.middlewares.authMiddleware import AuthMiddleware
from dotenv import load_dotenv
from app.morpion.infrastructure.socket_manager import setup_morpion_sockets
from geventwebsocket.handler import WebSocketHandler

app = Flask(__name__, template_folder='templates')
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


# ---------- Route ----------
@app.route('/')
def home():
    return "Page d'accueil de l'application Flask !"


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

# Ajouter un utilisateur à un chat
@app.route('/chat/add_users/<chat_id>', methods=['POST'])
@auth_middleware.require_authentication
def add_users_to_chat(chat_id):
    users_data = request.json
    users = users_data.get('users', [])
    chat_service = Chat()
    chat_service.add_users_to_chat(chat_id, users)
    return jsonify({"message": "Utilisateur ajouté au chat avec succès."}), 200


# Récupérer les messages d'un chat
@app.route('/chat/messages/<chat_id>', methods=['GET'])
@auth_middleware.require_authentication
def get_chat_messages(chat_id):
    chat_service = Chat()
    messages = chat_service.get_chat_messages(chat_id)
    return jsonify({"messages": messages}), 200


# Envoyer un message dans un chat
@app.route('/chat/send_message', methods=['POST'])
@auth_middleware.require_authentication
def send_message():
    message_data = request.json
    chat_id = message_data.get('chat_id')
    user_id = message_data.get('user_id')
    message = message_data.get('message')

    # Instancier le service Chat
    chat_service = Chat()

    # Utilise la méthode pour envoyer le message dans le chat
    chat_service.send_message(chat_id, {
        "user_id": user_id,
        "message": message
    })

    return jsonify(
        {"message": "Message envoyé avec succès dans le chat."}), 200


# ========================= SOCKETS =========================

@socketio.on('connect')
def connect():
    print(f'Le client {request.sid} est connecté')


@socketio.on('disconnect')
def disconnect():
    emit('disconnect')
    print(f'Le client {request.sid} est déconnecté')


@socketio.on('message')
def handle_message(data):
    message = data['message']
    username = data['username']
    print(
        f"L'utilisateur {request.sid} ({username}) a envoyé le message "
        f"suivant : {message}")
    # Enregistrer le message dans la base de données MongoDB
    chat_service = Chat()
    chat_service.send_message(
        {"Nom d'utilisateur": username, "message": message})
    socketio.emit('message',
                  {"Nom d'utilisateur": username, 'message': message})


if __name__ == '__main__':
    app.logger.setLevel(logging.ERROR)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    app.logger.addHandler(stream_handler)

    socketio.run(app, host='0.0.0.0', port=5000)
