from abc import ABC
from abc import abstractmethod


class UseCase(ABC):
    @abstractmethod
    def run(self, params):
        pass
