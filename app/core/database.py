from tortoise import Tortoise
from app.core.config import settings


TORTOISE_ORM = {
    "connections": {
        "default": settings.db_dsn,
    },
    "apps": {
        "models": {
            "models": ["app.bp.domain.user", "app.bp.domain.idempotency", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize database connection."""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    """Close database connection."""
    await Tortoise.close_connections()
