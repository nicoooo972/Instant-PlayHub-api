# app/application/game_service.py
# from app.domain.game import Game
from app.infrastructure.game_repository import GameRepository


class GameService:
    def __init__(self, game_repository):
        self.game_repository = game_repository

    def get_all_games(self):
        return self.game_repository.get_all()


game_service = GameService(GameRepository())
