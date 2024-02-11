# app.py

from flask import Flask, jsonify
from flask_cors import CORS
from app.application.game_service import game_service
from app.infrastructure.user import User

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return "Page d'accueil de l'application Flask !"

@app.route('/api/games')
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

if __name__ == '__main__':
    app.run()
    