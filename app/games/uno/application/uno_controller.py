from flask import Blueprint, request, jsonify
from ..domain.game import Game, GameOverReason
from ..domain.player import Player

uno_app = Blueprint('uno_app', __name__)
games = {}


@uno_app.route('/create_game', methods=['POST'])
def create_game():
    data = request.json
    room = data['room']
    player_names = data['players']
    players = {Player(name) for name in player_names}
    hand_size = data['hand_size']
    game = Game(room, players, hand_size)
    games[room] = game
    return jsonify({"message": "Game created", "room": room}), 201


@uno_app.route('/game_state/<room>', methods=['GET'])
def game_state(room):
    game = games.get(room)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    state = game.get_state()
    hands = {player.name: [card.__dict__ for card in cards] for player, cards
             in state[0].items()}
    top_card = state[1].__dict__
    return jsonify({"hands": hands, "top_card": top_card})


@uno_app.route('/draw_card/<room>/<player_id>', methods=['POST'])
def draw_card(room, player_id):
    game = games.get(room)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    game.draw(player_id)
    return jsonify({"message": f"Player {player_id} drew a card"})


@uno_app.route('/play_card/<room>/<player_id>/<card_id>', methods=['POST'])
def play_card(room, player_id, card_id):
    game = games.get(room)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    def on_game_over(reason, player):
        if reason == GameOverReason.WON:
            games.pop(room)
            return jsonify({"message": f"Player {player.name} won the game"})
        return jsonify({"message": f"Game over due to {reason.value}"})

    game.play(player_id, card_id, on_game_over)
    return jsonify({"message": f"Player {player_id} played {card_id}"})
