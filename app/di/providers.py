from app.bp.repository import UserReadRepository
from app.bp.repository import UserCreateRepository
from app.bp.repository import EncryptRepository

from app.bp import SignupUseCase
from app.bp import GetUserUseCase
from app.data import UserCreateRepositoryImp
from app.data import UserReadRepositoryImp
from app.data import EncryptRepositoryImp
from app.data import DataSource
from fastapi import Depends


def get_user_create_repository(
    data_source: DataSource = Depends(DataSource),
) -> UserCreateRepository:
    return UserCreateRepositoryImp(data_source)

def get_user_read_repository(
    data_source: DataSource = Depends(DataSource),
) -> UserReadRepository:
    return UserReadRepositoryImp(data_source)

def get_encrypt_repository(
) -> EncryptRepository:
    return EncryptRepositoryImp()

def get_get_user_use_case_module(
    user_read_repository: UserReadRepository = Depends(
        get_user_read_repository
    ),
) -> GetUserUseCase:
    return GetUserUseCase(user_read_repository)


def get_signup_use_case_module(
    user_create_repository: UserCreateRepository = Depends(
        get_user_create_repository
    ),
    user_read_repository: UserReadRepository = Depends(
        get_user_read_repository
    ),
    encrypt_repository: EncryptRepository = Depends(
        get_encrypt_repository
    ),
) -> SignupUseCase:
    return SignupUseCase(user_create_repository, user_read_repository, encrypt_repository)



