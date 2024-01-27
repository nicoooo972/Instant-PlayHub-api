from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from injector import inject
from application.game_service import GameService
from adapters.secondary.game_repository import GameRepository
from infrastructure.database.db import MongoDB


app = Flask(__name__, template_folder='templates')
CORS(app)


def configure(binder):
    binder.bind(GameRepository, to=GameRepository('./game.json'))
    binder.bind(GameService, to=GameService)


FlaskInjector(app=app, modules=[configure])

@app.route('/')
@inject
def index(game_service: GameService):
    games = game_service.get_all_games()
    return "Liste des jeux : {games}"

if __name__ == '__main__':
    app.run()
    