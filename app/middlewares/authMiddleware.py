# app/middlewares/authMiddleware.py

from functools import wraps
from flask import request, jsonify
import jwt
import os


class AuthMiddleware:

    def __init__(self, app):
        self.app = app
        self.secret_key = os.getenv("SECRET_KEY")

    def authenticate(self, token):
        try:
            decoded_token = jwt.decode(token, self.secret_key,
                                       algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            return None  # Le jeton a expiré
        except jwt.InvalidTokenError:
            return None  # Jeton invalide

    def require_authentication(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({
                                   "message": "Le jeton d'authentification "
                                              "est manquant !"}), 401
            decoded_token = self.authenticate(token)
            if not decoded_token:
                return jsonify({"message": "Jeton invalide ou expiré !"}), 401
            return f(*args, **kwargs)

        return decorated_function
