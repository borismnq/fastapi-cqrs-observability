from app.bp.repository import UserReadRepository
from app.bp.domain import UserReadModel
from uuid import UUID
from app.data.datasources import DataSource
from datetime import datetime


class UserReadRepositoryImp(UserReadRepository):
    def __init__(
        self,
        data_source: DataSource
    ) -> None:
        self.data_source = data_source

    async def get_user_by_id(
        self, id:UUID
    ) -> UserReadModel | None:
        return await self.data_source.get_user_by_id(id=id)
    
    async def project_to_read_model(
        self,
        id: UUID,
        name:str,
        email:str,
        display_name:str,
        created_at:datetime,
    ):
        await self.data_source.project_user_read_model(
            id=id,
            name=name,
            email=email,
            display_name=display_name,
            created_at=created_at,
        )
        