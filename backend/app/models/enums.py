"""Enumeration types."""

from enum import Enum


class DifficultyEnum(str, Enum):
    """Difficulty levels."""

    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"
    INSANE = "INSANE"
    EXPERT_PLUS = "EXPERT_PLUS"


class MappingStyleEnum(str, Enum):
    """Mapping styles."""

    TECHNICAL_STREAM = "TECHNICAL_STREAM"
    JUMP = "JUMP"
    HYBRID = "HYBRID"
    AIM = "AIM"
    STREAM_PRACTICE = "STREAM_PRACTICE"


class JobStatusEnum(str, Enum):
    """Job statuses."""

    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    ANALYZING = "ANALYZING"
    GENERATING = "GENERATING"
    PACKAGING = "PACKAGING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class HitObjectTypeEnum(str, Enum):
    """Hit object types in osu!"""

    CIRCLE = "CIRCLE"
    SLIDER = "SLIDER"
    SPINNER = "SPINNER"
