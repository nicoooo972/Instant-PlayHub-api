# morpion/application/game_service.py

class GameService:
    def __init__(self, board):
        self.board = board

    def start_new_game(self):
        self.board.reset_board()

    def make_move(self, player, row, col):
        # Check if it's the correct player's turn
        if self.board.get_current_player() != player:
            return False, "Ce n'est pas ton tour!"

        # Attempt to make the move on the board
        if not self.board.make_move(row, col):
            return False, "Mouvement invalide!"

        # Check for a winner or if the game is a draw
        winner = self.board.check_winner()
        if winner:
            return True, f"{winner} à gagné!"
        if self.board.is_full():
            return True, "Egalité!"

        # Switch players if no winner or draw
        self.board.switch_player()
        return True, "Mouvement accepté!"

    def get_game_state(self):
        return {
            'board': self.board.grid,
            'current_player': self.board.get_current_player(),
            'winner': self.board.check_winner(),
            'is_full': self.board.is_full()
        }
