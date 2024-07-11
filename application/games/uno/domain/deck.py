import random
from typing import List

from .card import Card


class Deck:
    SHUFFLE_FREQ = 50
    COLORS = ['rouge', 'blue', 'vert', 'jaune']
    NUMBER_CARDS = [str(i) for i in (list(range(0, 10)) + list(range(1, 10)))]
    DRAW_TWO_CARDS = ['draw-two'] * 2
    REVERSE_CARDS = ['reverse'] * 2
    SKIP_CARDS = ['skip'] * 2

    DRAW_FOUR_CARDS = ['draw-four'] * 4
    WILD_CARDS = ['wild'] * 4
    COLOR_CARDS = NUMBER_CARDS + DRAW_TWO_CARDS + REVERSE_CARDS + SKIP_CARDS

    def __init__(self):
        color_cards = [Card(color, value) for color in self.COLORS for value in
                       self.COLOR_CARDS]
        black_cards = [Card('black', value) for value in
                       (self.DRAW_FOUR_CARDS + self.WILD_CARDS)]

        self.cards: List[Card] = color_cards + black_cards
        self.shuffle()

    def get_cards(self) -> List[Card]:
        return self.cards

    def shuffle(self):
        for _ in range(self.SHUFFLE_FREQ):
            random.shuffle(self.cards)
