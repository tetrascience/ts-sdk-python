from uuid import uuid4

_next_uuid = str(uuid4())

def generate_uuid():
    global _next_uuid
    return_value = _next_uuid
    _next_uuid = str(uuid4())
    return return_value

def get_next_uuid():
    global _next_uuid
    return _next_uuid