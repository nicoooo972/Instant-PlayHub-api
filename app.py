import os
import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv

from application.infrastructure.user import User
from application.infrastructure.chat import Chat
from application.infrastructure.message import Message
from application.middlewares.authMiddleware import AuthMiddleware
from application.morpion.infrastructure.socket_manager import setup_morpion_sockets
from application.scores.infrastructure.score import Score
from application.rooms.domain.room import room_model

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

score_model = Score()

# ---------- Scores ----------

@app.route('/scores/game/<game_type>', methods=['GET'])
@jwt_required()
def get_scores_by_game(game_type):
    scores = score_model.get_scores_by_game(game_type)
    return jsonify(scores), 200

@app.route('/scores/user/<user_id>', methods=['GET'])
@jwt_required()
def get_scores_by_user(user_id):
    scores = score_model.get_scores_by_user(user_id)
    return jsonify(scores), 200


# ---------- Utilisateur ----------

@app.route('/')
def home():
    return "Page d'accueil de l'application Flask !"


@app.route('/create_room', methods=['POST'])
@jwt_required()
def create_generic_room():
    room_name = request.json.get('room_name')
    game_type = request.json.get('game_type')
    creator_id = request.json.get('creator_id')
    result = room_model.create_room(room_name, game_type, creator_id)
    room_id = result.inserted_id
    print("room id : ", room_id)
    socketio.emit('room_created', {'room': room_name, 'creator_id': creator_id,
                                   'game_type': game_type, 'room_id': room_id})
    return redirect(url_for('get_rooms', game_type=game_type))


@app.route('/rooms', methods=['GET'])
@jwt_required()
def get_rooms():
    game_type = request.args.get('game_type')
    rooms = room_model.get_rooms_by_game(game_type)
    return jsonify({"rooms": rooms, "game_type": game_type}), 200


@app.route('/join_room/<room>')
def player_join_room(room):
    room_data = room_model.get_rooms_by_game({"room_name": room})
    if room_data:
        game_type = room_data[0]['game_type']
        return redirect(url_for(game_type, room=room))
    return redirect(url_for('get_rooms', game_type='uno'))


@app.route('/delete_room', methods=['POST'])
@jwt_required()
def delete_room():
    room_name = request.json.get('room_name')
    creator_id = request.json.get('creator_id')
    result = room_model.delete_room(room_name, creator_id)
    if result and result.deleted_count == 1:
        return jsonify({"message": "Room deleted successfully"}), 200
    else:
        return jsonify({"message": "You are not authorized to delete this room"}), 403


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

# Supprimer un ami
@app.route('/friend/remove', methods=['POST'])
@jwt_required()
def remove_friend():
    data = request.json
    friend_id = data.get('friend_id')

    if not friend_id:
        return jsonify({"error": "friend_id est requis."}), 400

    user_service = User()  # si la méthode ne marche pas essayer avec la class Chat()
    return user_service.remove_friend(friend_id)

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
@jwt_required()
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
    message_data = request.json
    chat_id = message_data.get('chat_id')
    content = message_data.get('content')

    if not chat_id or not content:
        return jsonify({"error": "chat_id et content sont requis."}), 400

    # Instancier le service Message
    message_service = Message()

    # Utilise la méthode pour envoyer le message dans le chat
    return message_service.send_message(chat_id, content)

# Modifier un message dans un chat
@app.route('/chat/edit_message', methods=['PUT'])
@jwt_required()
def edit_message():
    message_data = request.json
    message_id = message_data.get('message_id')
    new_content = message_data.get('content')

    if not message_id or not new_content:
        return jsonify({"error": "message_id et content sont requis."}), 400

    # Instancier le service Message
    message_service = Message()

    # Utilise la méthode pour modifier le message
    return message_service.edit_message(message_id, new_content)

# Supprimer un message dans un chat
@app.route('/chat/delete_message', methods=['DELETE'])
@jwt_required()
def delete_message():
    message_data = request.json
    message_id = message_data.get('message_id')

    if not message_id:
        return jsonify({"error": "message_id est requis."}), 400

    # Instancier le service Message
    message_service = Message()

    # Utilise la méthode pour supprimer le message
    return message_service.delete_message(message_id)

# Supprimer un chat (supprime le chat uniquement pour l'utilisateur qui fait la requête)
@app.route('/chat/delete/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    chat = Chat()
    return chat.delete_chat(chat_id)


# ========================= SOCKETS =========================

@socketio.on('connect')
def connect():
    token = request.args.get('token')
    print(token)
    if token:
        try:
            # Simuler une requête HTTP pour vérifier le JWT
            request.headers = {'Authorization': f'Bearer {token}'}
            verify_jwt_in_request()
            user_email = get_jwt_identity()
            print(f'Le client {request.sid} est connecté en tant que {user_email}')
        except Exception as e:
            print(f'Erreur de connexion: {e}')
            return False  # Refuser la connexion si le token n'est pas valide
    else:
        print('Token JWT manquant')
        return False  # Refuser la connexion si le token est manquant


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
    print("test")
    token = data.get('token')
    if token:
        try:
            # Simuler une requête HTTP pour vérifier le JWT
            request.headers = {'Authorization': f'Bearer {token}'}
            verify_jwt_in_request()
            user_email = get_jwt_identity()

            chat_id = data['chat_id']
            content = data['content']
            sender = data['Sender']
            created_at = data['created_at']

            if not chat_id or not content:
                emit('error', {"error": "chat_id et content sont requis."})
                return

            message_service = Message()
            response, status = message_service.send_message(chat_id, content)

            if status == 200:
                socketio.emit('message', {
                        "chat_id": chat_id,
                        "content": content,
                        "Sender": sender,
                        "created_at": created_at
                    }, room=chat_id)
            else:
                emit('error', response.get_json())
        except KeyError as e:
            print(f'KeyError: {e}')
            emit('error', {"error": "Session is disconnected."})
        except Exception as e:
            print(f'Erreur de message: {e}')
            emit('error', {"error": "Token JWT invalide ou expiré."})
    else:
        emit('error', {"error": "Token JWT manquant."})


if __name__ == '__main__':
    app.logger.setLevel(logging.ERROR)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    app.logger.addHandler(stream_handler)
    socketio.run(app, host='0.0.0.0', port=5000, log_output=True)
