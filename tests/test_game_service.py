# tests/test_game_service.py
import unittest
from unittest.mock import Mock, patch
from application.game_service import GameService

class TestGameService(unittest.TestCase):
    @patch('application.game_service.GameRepository')
    def test_create_game(self, mock_game_repository):
        # Setup
        game_service = GameService(mock_game_repository)
        name = "Test Game"
        description = "This is a test game"
        version = "1.0"
        category = "Test Category"

        # Mock the behavior of save_game in the repository
        mock_game_repository.save_game.return_value = "mocked_game_id"

        # Call the create_game method
        created_game_id = game_service.create_game(name, description, version, category)

        # Assert that the repository method was called with the correct parameters
        mock_game_repository.save_game.assert_called_once_with(
            Mock(game_id=None, name=name, description=description, version=version, category=category)
        )

        # Assert that the returned game ID matches the mocked value
        self.assertEqual(created_game_id, "mocked_game_id")

if __name__ == '__main__':
    unittest.main()
