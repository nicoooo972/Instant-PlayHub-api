class Player:
    def __init__(self, name):
        self.id: str = f'player-{name}'
        self.name: str = name

    def __repr__(self) -> str:
        return f"Player(id={self.id}, name={self.name})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, obj) -> bool:
        return isinstance(obj, type(self)) and self.id == obj.id
