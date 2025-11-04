from abc import ABC
from abc import abstractmethod


class EncryptRepository(ABC):
    @abstractmethod
    async def encrypt(
        self, password: str
    ) -> str:
        pass