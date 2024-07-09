from constants.server import SERVER_NAMES_LOWER
from models.redis_cache import ServerInfo


def validate_server_name(server: str) -> bool:
    return server in SERVER_NAMES_LOWER


def validate_server_info_key(key: str) -> bool:
    return key in ServerInfo.model_fields.keys()
