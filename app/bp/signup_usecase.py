import uuid
from loguru import logger
from tortoise.exceptions import IntegrityError

from app.bp.repository import UserCreateRepository
from app.bp.repository import UserReadRepository
from app.bp.repository import EncryptRepository

from app.bp.domain import User
from app.schemas.user import SignupRequest
from app.infrastructure.metrics import signup_requests_total, signup_duplicates_total
from app.core.observability import get_tracer
from .usecase import UseCase

tracer = get_tracer(__name__)


class SignupUseCase(UseCase):
    def __init__(
        self,
        user_create_repository: UserCreateRepository,
        user_read_repository: UserReadRepository,
        encrypt_repository: EncryptRepository,
    ) -> None:
        self.user_create_repository = user_create_repository
        self.user_read_repository = user_read_repository
        self.encrypt_repository = encrypt_repository

    async def run(self, params: SignupRequest) -> User:
        """
        Create a new user.
        1. Validate business rules
        2. Hash password
        3. Create user in write model
        4. Project to read model
        
        Handled errors:
            ValueError: If email already exists
        """
        with tracer.start_as_current_span("SignupUseCase.run") as span:
            span.set_attribute("email", params.email)
            
            try:
                
                # check if already exists
                existing_user = await self.user_create_repository.get_user_by_email(email=params.email)
                if existing_user:
                    logger.warning(f"Duplicate signup attempt for email: {params.email}")
                    # metrics
                    signup_duplicates_total.inc()
                    signup_requests_total.labels(status="duplicate").inc()

                    raise ValueError(f"User with email {params.email} already exists")
                
                # encrypt password
                password_hash = await self.encrypt_repository.encrypt(params.password)
                
                # write model
                user = await self.user_create_repository.create_user(
                    id=uuid.uuid4(),
                    name=params.name,
                    email=params.email,
                    password_hash=password_hash,
                    display_name=params.display_name,
                )
                
                # proyection to read model
                await self.user_read_repository.project_to_read_model(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    display_name=user.display_name,
                    created_at=user.created_at,
                )
                
                logger.info(f"User created successfully: {user.id} ({user.email})")
                # metrics
                signup_requests_total.labels(status="success").inc()
                span.set_attribute("user_id", str(user.id))
                
                return user
                
            except IntegrityError as e:
                logger.error(f"Integrity error during signup: {str(e)}")
                # metrics
                signup_duplicates_total.inc()
                signup_requests_total.labels(status="duplicate").inc()
                raise ValueError(f"User with email {params.email} already exists")
            
            except Exception as e:
                logger.error(f"Error during SignupUseCase: {str(e)}")
                # metrics
                signup_requests_total.labels(status="error").inc()
                raise
