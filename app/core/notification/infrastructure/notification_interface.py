from abc import ABC, abstractmethod


class NotificationInterface(ABC):
    @abstractmethod
    def success(self, message: str):
        pass

    @abstractmethod
    def warn(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass
