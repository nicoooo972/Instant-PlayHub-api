from ..domain.game import Game, GameOverReason
from ..domain.player import Player
from ..infrastructure.notification import Notification
from ..domain.state import State

class GameService:
    def __init__(self, state: State):
        self.state = state

    def start_new_game(self, room, players, hand_size=7):
        notification = Notification(room)
        players_set = {Player(player_id) for player_id in players}
        game = Game(room, players_set, hand_size, notification)
        self.state.add_game_to_room(room, game)

    def draw_card(self, room, player_id):
        game = self.state.get_game_by_room(room)
        if game:
            game.draw(player_id)
            self.state.update_game_in_room(room, game)

    def play_card(self, room, player_id, card_id):
        game = self.state.get_game_by_room(room)
        if game:
            def on_game_over(reason, player):
                if reason == GameOverReason.WON:
                    self.state.delete_all(room)
                    return f"Player {player.name} won the game"
                return f"Game over due to {reason.value}"

            try:
                game.play(player_id, card_id, on_game_over)
                self.state.update_game_in_room(room, game)
            except ValueError:
                raise ValueError(f"Player with id {player_id} not found. Current players: {[player.id for player in game.players]}")

    def get_game_state(self, room):
        game = self.state.get_game_by_room(room)
        if game:
            state = game.get_state()
            hands = {player.id: [card.__dict__ for card in cards] for player, cards in state[0].items() if player is not None}
            top_card = state[1].__dict__
            return {
                'hands': hands,
                'top_card': top_card
            }
        return None
