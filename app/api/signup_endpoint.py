from fastapi import APIRouter,HTTPException, status, Depends
from app.schemas.user import SignupRequest, SignupResponse
from loguru import logger
from app.di import providers
from app.bp import SignupUseCase

router = APIRouter(prefix="", tags=["users"])


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED
)
async def signup(signup_request: SignupRequest,
    signup_use_case_module: SignupUseCase = Depends(
        providers.get_signup_use_case_module
    )):
    """
    Register a new user.
    Validations:
    - Email must be unique
    - Password must be at least 8 characters with uppercase, lowercase, and digit
    Headers:
    - `Idempotency-Key`: UUID to ensure idempotent processing
    - `X-Request-Id`: Request identifier for tracing
    - `X-Correlation-Id`: Correlation identifier for distributed tracing
    """
    try:
        user = await signup_use_case_module.run(signup_request)
        
        return SignupResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
        )
        
        
    except ValueError as e:
        logger.warning(f"Signup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )