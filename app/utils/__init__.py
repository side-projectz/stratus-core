import uuid
import logging
from datetime import datetime, timezone


logger = logging.getLogger("uvicorn")


def generate_uuid() -> uuid.UUID:
    _id = uuid.uuid4()
    return _id


def generate_timestamp():
    return (datetime.now(timezone.utc))


__all__ = ["logger", "generate_uuid", "generate_timestamp"]