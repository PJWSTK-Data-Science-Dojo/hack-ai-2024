import enum
from dataclasses import dataclass, field
from typing import List, Optional


class States(enum.Enum):
    WAITING_FOR_VIDEO_ID = 1
    WAITING_FOR_PROCESSED_DATA = 2
    VIEWING_SUMMARY = 3
    IDLE = 4
    DOESNT_EXISTS = 5


@dataclass
class Video:
    title: str
    process_id: str
    stage: str
    bullet_points: List[str] = field(default_factory=list)


@dataclass
class User:
    id: int
    state: States = States.IDLE
    videos: Optional[List[Video]] = field(default_factory=list)
    allowed_to_use: bool = True
