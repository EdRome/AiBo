from abc import ABC, abstractmethod

class Action(ABC):
    @abstractmethod
    def execute(self, memory, message: str, image: bytes = None):
        pass