from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserResponse
from app.di import providers
from loguru import logger
from uuid import UUID
from app.bp import GetUserUseCase


router = APIRouter(prefix="", tags=["users"])


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    
)
async def get_user(
    user_id: UUID,
    get_user_use_case_module: GetUserUseCase = Depends(
        providers.get_get_user_use_case_module
    )):
    """
    Get user by ID from read model.
    """
    try:
        user = await get_user_use_case_module.run(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        
        return UserResponse.model_validate(user)
    except Exception as exception:
        logger.error(f"Unexpected error during get_user: {str(exception)}")
        raise exception