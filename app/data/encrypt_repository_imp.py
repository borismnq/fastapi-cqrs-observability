from passlib.hash import bcrypt
from app.bp.repository import EncryptRepository


class EncryptRepositoryImp(EncryptRepository):
    def __init__(
        self,
    ) -> None:
        pass

    async def encrypt(
        self, password: str
    ) -> str:
        return bcrypt.hash(password)