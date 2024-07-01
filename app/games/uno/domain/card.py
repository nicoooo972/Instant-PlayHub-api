class Card:
    def __init__(self, color, value):
        self.id: str = f'{value}-{color}'
        self.color: str = color
        self.value: str = value

    def is_special(self) -> bool:
        special_cards = {'draw-two', 'reverse', 'skip', 'draw-four', 'wild'}
        return self.value in special_cards or self.color == 'black'

    def is_black(self) -> bool:
        return self.color == 'black'

    def is_draw_four(self) -> bool:
        return self.value == 'draw-four'

    def is_wild(self) -> bool:
        return self.value == 'wild'

    def __repr__(self) -> str:
        return f'Card(color={self.color}, value={self.value})'
