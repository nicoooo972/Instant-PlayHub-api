import unittest

from app.morpion.application.game_service import GameService
from app.morpion.domain import board


class TestGameService(unittest.TestCase):
    def setUp(self):
        self.board = board.Board()
        self.game_service = GameService(self.board)

    def test_start_new_game(self):
        self.game_service.start_new_game()
        expected_empty_board = [['' for _ in range(3)] for _ in range(3)]
        self.assertEqual(self.board.grid, expected_empty_board,
                         "Board should be reset")

    def test_make_move_valid(self):
        self.game_service.start_new_game()
        success, message = self.game_service.make_move('X', 0, 0)
        self.assertTrue(success, "Move should be successful")
        self.assertEqual(self.board.grid[0][0], 'X',
                         "X should be placed on the board")

    def test_make_move_invalid_spot(self):
        self.game_service.start_new_game()
        self.game_service.make_move('X', 0, 0)
        success, message = self.game_service.make_move('X', 0, 0)
        self.assertFalse(success,
                         "Move should not be successful on an occupied spot")

    def test_make_move_out_of_turn(self):
        self.game_service.start_new_game()
        success, message = self.game_service.make_move('O', 0, 0)
        self.assertFalse(success,
                         "Move should not be successful when out of turn")

    def test_make_move_check_winner(self):
        self.game_service.start_new_game()
        self.game_service.make_move('X', 0, 0)
        self.game_service.make_move('O', 1, 0)
        self.game_service.make_move('X', 0, 1)
        self.game_service.make_move('O', 1, 1)
        success, message = self.game_service.make_move('X', 0, 2)
        self.assertTrue(success, "Move should be successful")
        self.assertEqual(message, 'X wins!', "X should be the winner")

    def test_make_move_check_draw(self):
        self.game_service.start_new_game()
        moves = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (1, 1), (2, 1),
                 (2, 2), (2, 0)]
        players = ['X', 'O'] * 5
        for move, player in zip(moves, players):
            success, message = self.game_service.make_move(player, *move)
            if message == "Draw!":
                break
        self.assertTrue(success, "Move should be successful")
        self.assertEqual(message, 'Draw!', "The game should end in a draw")

    def test_get_game_state(self):
        self.game_service.start_new_game()
        self.game_service.make_move('X', 0, 0)
        state = self.game_service.get_game_state()
        self.assertEqual(state['current_player'], 'O',
                         "Next player should be O after X's move")
        self.assertEqual(state['board'][0][0], 'X',
                         "Board should reflect the move made")

# Code to run the unittests (commented out to prevent execution in the PCI)
# if __name__ == '__main__':
#     unittest.main()
