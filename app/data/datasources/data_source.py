
from app.bp.domain import User
from app.bp.domain import UserReadModel
from uuid import UUID
from datetime import datetime


class DataSource:
    def __init__(self):
        pass
    
    async def get_user_by_id(
        self, id:UUID
    ) -> UserReadModel | None:
        return await UserReadModel.get_or_none(id=id)
    
    async def get_user_by_email(
        self, email:str
    ) -> User | None:
        return await User.get_or_none(email=email)

    async def create_user(
        self,
        id: UUID,
        name:str,
        email:str,
        password_hash:str,
        display_name:str
    ) -> User:
        return await User.create(
            id=id,
            name=name,
            email=email,
            password_hash=password_hash,
            display_name=display_name,
        )

    async def project_user_read_model(
        self,
        id: UUID,
        name:str,
        email:str,
        display_name:str,
        created_at:datetime,
    ):
        await UserReadModel.create(
            id=id,
            name=name,
            email=email,
            display_name=display_name,
            created_at=created_at,
        )