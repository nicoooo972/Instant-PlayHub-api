from flask import Flask, jsonify
from flask_cors import CORS
from app.application.game_service import game_service

app = Flask(__name__, template_folder='templates')
CORS(app)



@app.route('/api/games')
def getGames():
    games = game_service.get_all_games()
    return jsonify({'games': games})

if __name__ == '__main__':
    app.run()
    