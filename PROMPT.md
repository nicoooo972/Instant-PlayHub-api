# Application Flask

## Technologies

- Python
- Flask
- MongoDB

## Architecture de l'application

  ```markdown
  app/application/_init_.py
  app/application/chat_service.py
  app/application/game_service.py
  app/application/score_service.py
  app/application/user_service.py
  app/domain/_init_.py
  app/domain/chat_message.py
  app/domain/game.py
  app/domain/score.py
  app/domain/user.py
  app/infrastructure/_init_.py
  app/infrastructure/game_repository.py
  app/_init_.py
  flask/bin
  flask/lib
  templates/index.html
  tests/test_game_service.py
  test_user_service.py
  app.py
  db.py
  requirements.txt
  venv
  .env
  ```
  
## Ma demande

J'ai un chat en base de données, je souhaite ajouter un nouvel utilisateur dans ce chat, cependant j'ai une erreur que je ne comprends pas sur POSTMAN.
Aide-moi à comprendre ce qui ne va pas :

```py
# app/infrastructure/chat.py

from db import db
from datetime import datetime
import uuid
from flask import jsonify, request

# Modèle d'un chat
class Chat:
    def send_message(self, message_data):
        db.message.insert_one(message_data) # Enregistrer le message dans la base de données MongoDB

    def get_messages(self):
        messages = list(db.message.find()) # Récupérer l'historique des messages depuis la base de données MongoDB
        return messages

    def create_chat(self, name, users):
        now = datetime.now() # Date de création du chat
        created_at = now.strftime("%d/%m/%Y %H:%M:%S") # Formatage de la date -> dd/mm/YY H:M:S
        
        chat_data = {
            "_id": uuid.uuid4().hex,
            "name": name,
            "Users": users,
            "Messages": [],
            "created_at": created_at
        }
        db.chat.insert_one(chat_data)

    # Méthode pour ajouter des utilisateurs à un chat existant
    def add_users_to_chat(self, chat_id, users):
        db.chat.update_one({"_id": chat_id}, {"$addToSet": {"users": {"$each": users}}})

    # Méthode pour récupérer les messages d'un chat spécifique
    def get_chat_messages(self, chat_id):
        chat = db.chat.find_one({"_id": chat_id})
        if chat:
            return chat["messages"]
        else:
            return []
```

```py
# app.py

import os
import logging
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
def home():
    return "Page d'accueil de l'application Flask !"

# Liste des jeux
@app.route('/api/games')
@auth_middleware.require_authentication
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
    return user.logout()

# Créer un chat
@app.route('/chat/create', methods=['POST'])
@auth_middleware.require_authentication
def create_chat():
    chat_data = request.json
    users = chat_data.get('users', [])
    chat_service = Chat()
    chat_service.create_chat(users)
    return jsonify({"message": "Chat créé avec succès"}), 200

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
    print(f"L'utilisateur {request.sid} ({username}) a envoyé le message suivant : {message}")
    # Enregistrer le message dans la base de données MongoDB
    chat_service = Chat()
    chat_service.send_message({"Nom d'utilisateur": username, "message": message})
    socketio.emit('message', {"Nom d'utilisateur": username, 'message': message})

if __name__ == '__main__':
    app.run(debug=True)
    
# Configurer le niveau de logging pour enregistrer uniquement les messages d'erreur et les messages critiques
app.logger.setLevel(logging.ERROR)

# Ajouter un gestionnaire de console pour afficher les logs d'erreur dans la console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
app.logger.addHandler(stream_handler)
    
```

```py
# app/infrastructure/user.py

import logging
from flask import jsonify, request
import uuid
import os
from passlib.hash import pbkdf2_sha256
from db import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

# Modèle d'utilisateur
class User:
    # Création compte utilisateur
    def register(self):
        user_data = request.json
        
        # Date de création de l'utilisateur
        now = datetime.now()
        # Formatage de la date -> dd/mm/YY H:M:S
        created_at = now.strftime("%d/%m/%Y %H:%M:%S")

        user = {
            "_id": uuid.uuid4().hex,
            "username": user_data.get('username'),
            "email": user_data.get('email'),
            "password": user_data.get('password'),
            "created_at": created_at
        }

        if secret_key is None:
            return jsonify({"error": "La clé secrète n'est pas définie !"}), 500

        try:
            secret_key_bytes = secret_key.encode('utf-8')
        except Exception as e:
            return jsonify({"error": "Erreur lors de l'encodage de la clé secrète en bytes !", "details": str(e)}), 500

        user["password"] = pbkdf2_sha256.hash(user['password'], salt=secret_key_bytes)

        if db.user.find_one({"email": user["email"]}):
            return jsonify({"error": "Cette adresse Email est déjà utilisée par un utilisateur !"}), 400
  
        if db.user.insert_one(user):
            return jsonify(user), 200

        return jsonify({"error": "L'inscription a échouée."}), 400
    
    # Connexion compte utilisateur
    def login(self):
        login_data = request.json
        email = login_data.get('email')
        password = login_data.get('password')
        
        user = db.user.find_one({"email": email})
        if user and pbkdf2_sha256.verify(password, user['password']):
            access_token = create_access_token(identity=email, expires_delta=timedelta(hours=24))  # Création du token JWT avec l'email de l'utilisateur
            logging.info(f"Connexion réussie pour l'utilisateur avec l'email {email}.")
            return jsonify({"message": "Vous êtes connecté ! ", "Token de connexion : ": access_token}), 200  # Retourner le token dans la réponse JSON
        else:
            logging.error("Tentative de connexion échouée.")
            return jsonify({"error": "Adresse Email ou mot de passe incorrect !"}), 401
    
    # Déconnexion compte utilisateur avec expiration du token JWT
    @jwt_required()
    def logout(self):
        unset_jwt_cookies()  # Expiration du token JWT
        return jsonify({"message": "Vous êtes déconnecté."}), 200

  
user = User()
```

Je ne pense pas avoir de route pour envoyer un message dans un chat, si j'en ai une utilise-là pour envoyer un message dans un chat.


Base de données :

```json
{
    _id: 'ccfb31a6f10843aaaab957670afcd297',
    Users: [
      '2c4516aa1e5545858fa0eb177814708d',
      '0449ba70ec9244f296d46200eb16907f'
    ],
    Messages: [],
    created_at: ISODate('2024-03-24T23:10:15.772Z'),
    name: 'Chat test'
  }
```

Postman :

```json
URL : http://127.0.0.1:5000/chat/add_users/ccfb31a6f10843aaaab957670afcd297

Body :

{
    "_id": "ccfb31a6f10843aaaab957670afcd297",
    "Users": ["d7f8142ee1e64891baba235079700256"]
}

<!doctype html>
<html lang=en>
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)</p>
```

Assurez-vous que la méthode add_users_to_chat de la classe Chat fonctionne correctement. Vous pouvez essayer d'appeler cette méthode avec des paramètres statiques directement depuis votre application Flask pour voir si elle fonctionne comme prévu.

## À FAIRE

- Utilisateut : Paramètres utilisateurs (changer informations du profile)
- Chat : CRUD messages, CRUD chat
