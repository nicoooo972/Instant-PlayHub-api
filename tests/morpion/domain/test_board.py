import unittest

from application.morpion.domain import board


class TestBoardDebug(unittest.TestCase):
    def setUp(self):
        self.board = board.Board()

    def test_make_move_valid(self):
        self.assertTrue(self.board.make_move(0, 0))
        self.assertEqual(self.board.grid[0][0], 'X')

    def test_make_move_invalid(self):
        self.board.make_move(0, 0)
        self.assertFalse(self.board.make_move(0, 0))

    def test_switch_player(self):
        self.board.make_move(0, 0)
        self.board.switch_player()
        self.assertEqual(self.board.current_player, 'O')

    def test_full_board_draw(self):
        moves = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (1, 1), (2, 1),
                 (2, 2), (2, 0)]
        players = ['X', 'O', 'X', 'O', 'X', 'O', 'X', 'O', 'X']
        for move, player in zip(moves, players):
            self.board.current_player = player
            self.board.make_move(*move)
        for row in self.board.grid:
            print(row)
        self.assertIsNone(self.board.check_winner())
        self.assertTrue(self.board.is_full())

    def test_reset_board(self):
        self.board.make_move(0, 0)
        self.board.reset_board()
        self.assertTrue(
            all(all(cell == '' for cell in row) for row in self.board.grid))
        self.assertEqual(self.board.current_player, 'X')
