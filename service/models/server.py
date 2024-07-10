from pydantic import BaseModel

from models.character import Character
from models.lfm import LFM

# class UpdateTimestamps(BaseModel):
#     lfms: float | None = None
#     characters: float | None = None
#     server_status: float | None = None
#     created: float | None = None


class Server(BaseModel):
    name: str
    index: int | None = None
    status: dict | None = None
    created: float | None = None
    characters: list[Character] | None = None
    lfms: list[LFM] | None = None
    # character_count: int | None = None
    # lfm_count: int | None = None
