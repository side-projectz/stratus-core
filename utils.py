import uuid

def generate_uuid() -> uuid.UUID:
    _id = uuid.uuid4()
    return _id