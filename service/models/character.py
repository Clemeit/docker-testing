from typing import Union

from pydantic import BaseModel


class CharacterClass(BaseModel):
    name: str
    level: int


class CharacterLocation(BaseModel):
    name: str
    region: Union[str, None]
    is_public_space: bool


class Character(BaseModel):
    id: str
    name: str
    gender: str
    race: str
    guild: Union[str, None]
    classes: list[CharacterClass]
    total_level: int
    group_id: Union[str, None]
    is_in_party: bool
    location: CharacterLocation
    home_server: Union[str, None]
    server: str
    is_recruiting: bool
