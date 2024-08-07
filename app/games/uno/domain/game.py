import collections
import random
from typing import Any, Callable, DefaultDict, List, Set, Tuple

from .card import Card
from .deck import Deck
from .player import Player
from enum import Enum

from ..infrastructure.notification import Notification


class GameOverReason(Enum):
    WON = 'won'
    ERROR = 'error'
    INSUFFICIENT_PLAYERS = 'insufficient-players'


class Game:
    MIN_PLAYERS_ALLOWED = 2
    MAX_PLAYERS_ALLOWED = 4

    def __init__(self, room: str, players: Set[Player], hand_size: int):
        self.hands: DefaultDict[Player, List[Card]] = collections.defaultdict(list)
        self.players: Set[Player] = players
        self.notify = Notification(room)
        self.deck = Deck()

        self.validate_players()

        cards = self.deck.get_cards()

        TOTAL_PLAYERS = len(players)
        self.remaining_cards: List[Card] = cards[TOTAL_PLAYERS * hand_size:]
        player_cards = cards[:TOTAL_PLAYERS * hand_size]

        # Distribute cards (alternatively)
        i = 0
        while i < len(player_cards):
            for player in players:
                self.hands[player].append(player_cards[i])
                i += 1

        # Pick a top card (skip special cards)
        top_card = random.choice(self.remaining_cards)
        while top_card.is_special():
            top_card = random.choice(self.remaining_cards)

        self.game_stack: List[Card] = [top_card]

    def remove_player(self, player) -> None:
        self.players.remove(player)

    def validate_players(self) -> None:
        if len(self.players) < self.MIN_PLAYERS_ALLOWED:
            raise Exception(f"need at least {self.MIN_PLAYERS_ALLOWED} players to start the game")
            return

    def get_state(self) -> Tuple[DefaultDict[Player, List[Card]], Card]:
        self.validate_players()
        top_card = self.get_top_card()

        return self.hands, top_card

    def get_top_card(self) -> Card:
        return self.game_stack[-1]

    def transfer_played_cards(self) -> None:
        played_cards = self.game_stack[::]
        played_cards.pop()  # Remove the top card

        random.shuffle(played_cards)  # Shuffle played card
        self.remaining_cards = played_cards[::]
        self.game_stack = [self.get_top_card()]

    def draw(self, player_id: str) -> None:
        self.validate_players()

        player = self.find_object(self.players, player_id)
        player_cards = self.hands[player]

        if not self.remaining_cards:
            self.transfer_played_cards()

        if not self.remaining_cards:
            self.notify.warn('deck is empty!')
            return

        new_card = self.remaining_cards.pop()
        player_cards.append(new_card)

    def play(self, player_id: str, card_id: str, on_game_over: Callable[[GameOverReason, Any], None]) -> None:
        self.validate_players()

        player = self.find_object(self.players, player_id)
        player_cards = self.hands[player]
        card = self.find_object(player_cards, card_id)
        top_card = self.get_top_card()

        def execute_hand():
            nonlocal player_cards, card

            # Find and remove card from the current player's hand
            idx = self.find_object_idx(player_cards, card.id)
            player_cards.pop(idx)

            # Insert played card top of the game stack
            self.game_stack.append(card)

            if len(player_cards) == 1:
                self.notify.success(f"UNO! by {player.name}")

            if len(player_cards) == 0:
                on_game_over(GameOverReason.WON, player)

        # Can play any card on top of black cards
        if not card.is_black() and top_card.is_black():
            execute_hand()
            return

        if card.is_black() and top_card.is_black():
            # Cannot play wild card on top of draw four and vice-versa
            if ((card.is_draw_four() and top_card.is_wild()) or
                    (card.is_wild() and top_card.is_draw_four())):
                self.notify.error(
                    f"cannot play a {card.value} card on top of a {top_card.value} card")
                return
            execute_hand()
            return

        same_color = card.color == top_card.color
        same_value = card.value == top_card.value

        if same_color or same_value:
            execute_hand()
            return

        if card.is_black():
            execute_hand()
            return

    def find_object(self, objects, obj_id: str):
        objects = list(objects)
        idx = self.find_object_idx(objects, obj_id)

        return objects[idx]

    def find_object_idx(self, objects, obj_id: str):
        return [obj.id for obj in objects].index(obj_id)