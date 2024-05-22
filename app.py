# app.py

import os
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from gevent import pywsgi

from app.application.game_service import game_service
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
def index():
    return render_template('index.html')


@app.route('/morpion')
def morpion():
    return render_template('morpion.html')


@app.route('/rooms')
def rooms():
    return render_template('rooms.html')


if __name__ == '__main__':
    app.logger.setLevel(logging.ERROR)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    app.logger.addHandler(stream_handler)

    socketio.run(app, host='0.0.0.0', port=5000)
