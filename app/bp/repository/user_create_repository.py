from abc import ABC
from abc import abstractmethod
from uuid import UUID
from app.bp.domain import User

class UserCreateRepository(ABC):
    @abstractmethod
    async def get_user_by_email(
        self, email:str
    ) -> User | None:
        pass
    
    @abstractmethod
    async def create_user(
        self,
        id: UUID,
        name:str,
        email:str,
        password_hash:str,
        display_name:str
    ) -> User:
        pass
    