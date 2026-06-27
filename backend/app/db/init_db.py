import logging

from app.db.base_class import Base
from app.db.session import engine
import app.models  # noqa: F401  ensures all models are registered on Base.metadata

logger = logging.getLogger(__name__)


def init_db() -> None:
    logger.info("Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    init_db()