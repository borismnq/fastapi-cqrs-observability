import uuid
from loguru import logger
from app.bp.repository import UserReadRepository

from app.bp.domain import UserReadModel
from app.core.observability import get_tracer
from .usecase import UseCase


tracer = get_tracer(__name__)


class GetUserUseCase(UseCase):
    def __init__(
        self,
        user_read_repository: UserReadRepository,
    ) -> None:
        self.user_read_repository = user_read_repository

    async def run(self, user_id: uuid.UUID) -> UserReadModel | None:
        """
        Get user by id.
        
        Handled cases:
            Warning log: If user not found
        """
        with tracer.start_as_current_span("GetUserUseCase.run") as span:
            span.set_attribute("user_id", str(user_id))
            try:
                
                user = await self.user_read_repository.get_user_by_id(id=user_id)
                if user:
                    logger.info(f"User retrieved: {user_id}")
                else:
                    logger.warning(f"User not found: {user_id}")
            except Exception as e:
                logger.error(f"Error during GetUserUseCase: {str(e)}")
                raise
            
            return user