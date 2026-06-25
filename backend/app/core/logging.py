import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
        stream=sys.stdout,
    )

    # Приглушить шумные библиотеки
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
