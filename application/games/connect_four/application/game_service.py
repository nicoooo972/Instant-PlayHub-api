from application.games.connect_four.domain.board import ConnectFour


class GameService:
    def __init__(self):
        self.game = ConnectFour()

    def drop_piece(self, column):
        if self.game.drop_piece(column):
            if self.game.check_winner():
                return {"winner": self.game.current_player}
            elif self.game.is_draw():
                return {"draw": True}
            else:
                self.game.switch_player()
                return {"board": self.game.board,
                        "current_player": self.game.current_player}
        return {"error": "Invalid move"}

    def get_board(self):
        return {"board": self.game.board,
                "current_player": self.game.current_player}
