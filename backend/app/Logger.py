import logging
from app.config import get_settings


settings = get_settings()


def _configure_root_logger() -> logging.Logger:
    level_name = settings.LOG_LEVEL
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    logger = logging.getLogger("bookitgy")
    logger.debug("Logger initialized with level %s", level_name)
    return logger


logger = _configure_root_logger()

__all__ = ["logger"]
