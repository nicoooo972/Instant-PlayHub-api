# application/game_service.py
from domain.game import Game

class GameService:
    def __init__(self, game_repository):
        self.game_repository = game_repository

    def create_game(self, name, description, version, category):
        game = Game(game_id=None, name=name, description=description, version=version, category=category)
        game_id = self.game_repository.save_game(game)
        return game_id

    def get_game_by_id(self, game_id):
        return self.game_repository.get_game_by_id(game_id)

    def get_all_games(self):
        return self.game_repository.get_all_games()