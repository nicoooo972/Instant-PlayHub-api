from abc import ABC, abstractmethod


class GameInterface(ABC):
    @abstractmethod
    def won(self, message: str):
        pass

    @abstractmethod
    def lost(self, message: str):
        pass

    @abstractmethod
    def insufficient_players(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass

    @abstractmethod
    def end_game(self, message: str):
        pass

