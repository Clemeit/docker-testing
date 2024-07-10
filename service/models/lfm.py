from pydantic import BaseModel

from models.character import Character


class QuestLevel(BaseModel):
    heroic_normal: int | None = None
    heroic_hard: int | None = None
    heroic_elite: int | None = None
    epic_normal: int | None = None
    epic_hard: int | None = None
    epic_elite: int | None = None


class QuestXP(BaseModel):
    heroic_normal: int | None = None
    heroic_hard: int | None = None
    heroic_elite: int | None = None
    epic_normal: int | None = None
    epic_hard: int | None = None
    epic_elite: int | None = None


class Quest(BaseModel):
    id: str
    alt_id: str | None = None
    area_id: str | None = None
    name: str
    level: QuestLevel
    xp: QuestXP
    is_free_to_play: bool
    is_free_to_vip: bool
    required_adventure_pack: str | None = None
    adventure_area: str | None = None
    quest_journal_group: str | None = None
    group_size: str
    patron: str | None = None
    average_time: int | None = None
    tip: str | None = None


class LFM(BaseModel):
    id: str
    comment: str | None = None
    quest: Quest | None = None
    is_quest_guess: bool
    difficulty: str | None = None
    accepted_classes: list[str] | None = None
    accepted_classes_count: int
    minimum_level: int
    maximum_level: int
    adventure_active_time: int | None = None
    leader: Character
    members: list[Character] | None = None
