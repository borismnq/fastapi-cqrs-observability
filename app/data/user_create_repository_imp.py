from app.bp.repository import UserCreateRepository
from app.bp.domain import User
from uuid import UUID
from app.data.datasources import DataSource

class UserCreateRepositoryImp(UserCreateRepository):
    def __init__(
        self,
        data_source: DataSource
    ) -> None:
        self.data_source = data_source

    
    async def get_user_by_email(
        self, email:str
    ) -> User | None:
        return await self.data_source.get_user_by_email(email=email)
    
    
    async def create_user(
        self,
        id: UUID,
        name:str,
        email:str,
        password_hash:str,
        display_name:str
    ) -> User:
        return await self.data_source.create_user(
            id=id,
            name=name,
            email=email,
            password_hash=password_hash,
            display_name=display_name
        )
        
        