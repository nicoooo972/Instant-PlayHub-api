# app.py

import os
import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from gevent import pywsgi

import db
from app.games.uno.domain.state import State
from app.infrastructure.user import User
from app.infrastructure.chat import Chat
from flask_jwt_extended import JWTManager, get_jwt_identity, \
    verify_jwt_in_request
from flask_socketio import SocketIO, emit
from app.middlewares.authMiddleware import AuthMiddleware
from dotenv import load_dotenv
from app.morpion.infrastructure.socket_manager import setup_morpion_sockets
from geventwebsocket.handler import WebSocketHandler
from flask_jwt_extended import jwt_required
from app.games.uno.infrastructure.socket_manager import setup_uno_sockets
from app.rooms.domain.room import room_model

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

state = State()

# ---------- Setup ----------
setup_morpion_sockets(socketio)
setup_uno_sockets(socketio)


# ---------- Utilisateur ----------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/create_room', methods=['POST'])
@jwt_required()
def create_generic_room():
    room_name = request.form['room_name']
    game_type = request.form['game_type']
    creator_id = request.form['creator_id']
    room_model.create_room(room_name, game_type, creator_id)
    return redirect(url_for('get_rooms', game_type=game_type))


@app.route('/rooms')
def get_rooms():
    game_type = request.args.get('game_type')
    token = request.args.get('token')
    request.headers = {"Authorization": f"Bearer {token}"}
    verify_jwt_in_request()
    rooms = room_model.get_rooms_by_game(game_type)
    return render_template('rooms.html', rooms=rooms, game_type=game_type)


@app.route('/join_room/<room>')
def join_room(room):
    room_data = room_model.get_rooms_by_game({"room_name": room})
    if room_data:
        game_type = room_data[0]['game_type']
        return redirect(url_for(game_type, room=room))
    return redirect(url_for('get_rooms',
                            game_type='uno'))


@app.route('/delete_room', methods=['POST'])
@jwt_required()
def delete_room():
    room_name = request.form['room_name']
    creator_id = request.form['creator_id']
    result = room_model.delete_room(room_name, creator_id)
    if result and result.deleted_count == 1:
        return jsonify({"message": "Room deleted successfully"}), 200
    else:
        return jsonify({"message": "You are not authorized to delete this room"}), 403


# ---------- Jeux ----------


@app.route('/uno')
def uno():
    room_name = request.args.get('room')
    return render_template('uno.html', room_name=room_name)


@app.route('/morpion')
def morpion():
    room_name = request.args.get('room')
    return render_template('morpion.html', room_name=room_name)


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


# Déconnexion compte utilisateur
@app.route('/logout', methods=['POST'])
def logout():
    user = User()
    return user.logout()


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
