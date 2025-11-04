from abc import ABC
from abc import abstractmethod
from uuid import UUID
from app.bp.domain import UserReadModel
from datetime import datetime

class UserReadRepository(ABC):
    @abstractmethod
    async def get_user_by_id(
        self, id:UUID
    ) -> UserReadModel | None:
        pass
    
    @abstractmethod
    async def project_to_read_model(
        self,
        id: UUID,
        name:str,
        email:str,
        display_name:str,
        created_at:datetime,
    ):
        pass
    