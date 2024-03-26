# app.py

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from app.application.game_service import game_service
from app.infrastructure.user import User
from app.infrastructure.chat import Chat
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from app.middlewares.authMiddleware import AuthMiddleware
from dotenv import load_dotenv

app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialisation du middleware
auth_middleware = AuthMiddleware(app)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de la clé secrète pour les tokens JWT
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins='*')

# ========== ROUTES ==========

# Page d'accueil
@app.route('/')
@auth_middleware.require_authentication
def home():
    return "Page d'accueil de l'application Flask !"

# Liste des jeux
@app.route('/api/games')
#
def getGames():
    games = game_service.get_all_games()
    return jsonify({'games': games})

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
    return user.logout() # la méthode logout() de la classe User sera appelée, ce qui renverra une réponse JSON indiquant que la déconnexion a été réussie.

# Créer un chat
@app.route('/chat/create', methods=['POST'])
def create_chat():
    chat_data = request.json
    users = chat_data.get('users', [])
    chat_service = Chat()
    chat_service.create_chat(users)
    return jsonify({"message": "Chat créé avec succès"}), 200

# Ajouter un utilisateur à un chat
@app.route('/chat/<chat_id>/add_users', methods=['POST'])
def add_users_to_chat(chat_id):
    users_data = request.json
    users = users_data.get('users', [])
    chat_service = Chat()
    chat_service.add_users_to_chat(chat_id, users)
    return jsonify({"message": "Utilisateur ajouté au chat avec succès."}), 200

# Récupérer les messages d'un chat
@app.route('/chat/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    chat_service = Chat()
    messages = chat_service.get_chat_messages(chat_id)
    return jsonify({"messages": messages}), 200


# ========== SOCKETS ==========

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
    print(f'Le cient {request.sid} ({username}) envoie un message : {message}')
    # Enregistrer le message dans la base de données MongoDB
    chat_service = Chat()
    chat_service.send_message({"Nom d'utilisateur": username, "message": message})
    socketio.emit('message', {"Nom d'utilisateur": username, 'message': message})

if __name__ == '__main__':
    app.run(debug=True)
    