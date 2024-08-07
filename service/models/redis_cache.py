from pydantic import BaseModel
from typing import Optional
from models.character import Character
from models.lfm import LFM
from constants.server import SERVER_NAMES_LOWER


class ServerInfo(BaseModel):
    """
    This model will be used to store information about each server in the redis database using reJSON.
    """

    index: Optional[int] = None
    created: Optional[float] = None
    last_status_check: Optional[float] = None
    last_data_fetch: Optional[float] = None
    is_online: Optional[bool] = None
    character_count: Optional[int] = None
    lfm_count: Optional[int] = None


class GameInfo(BaseModel):
    """
    This model will be used to store information about the game in the redis database using reJSON.
    """

    servers: dict[str, ServerInfo] = {}


class ServerCharacters(BaseModel):
    """
    This model will be used to store information about each server's characters in the redis database using reJSON.
    """

    characters: dict[str, Character] = {}
    character_count: int = 0
    last_updated: Optional[float] = None


class ServerLFMs(BaseModel):
    """
    This model will be used to store information about each server's LFMs in the redis database using reJSON.
    """

    lfms: dict[str, LFM] = {}
    lfm_count: int = 0
    last_updated: Optional[float] = None


CACHE_MODEL = {
    "game_info": GameInfo(),
    **{f"characters:{server}": ServerCharacters() for server in SERVER_NAMES_LOWER},
    **{f"lfms:{server}": ServerLFMs() for server in SERVER_NAMES_LOWER},
}
