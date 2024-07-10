from pydantic import BaseModel

from models.character import Character
from models.lfm import LFM


class ServerInfo(BaseModel):
    """
    This model will be used to store information about each server in the redis database using reJSON.
    <server_name>:<info>
    """

    index: int | None = None
    created: float | None = None
    last_updated: float | None = None
    status: bool | None = None


class ServerCharacters(BaseModel):
    """
    This model will be used to store information about each server's characters in the redis database using reJSON.
    <server_name>:<characters>
    """

    characters: dict[str, Character] = {}
    character_count: int = 0
    last_updated: float | None = None


class ServerLFMs(BaseModel):
    """
    This model will be used to store information about each server's LFMs in the redis database using reJSON.
    <server_name>:<lfms>
    """

    lfms: dict[str, LFM] = {}
    lfm_count: int = 0
    last_updated: float | None = None
