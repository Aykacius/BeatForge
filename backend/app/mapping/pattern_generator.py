"""Pattern generation logic."""

import logging
import random

import numpy as np

from app.models.enums import MappingStyleEnum
from app.mapping.cursor_momentum import CursorMomentum

logger = logging.getLogger(__name__)


class PatternGenerator:
    """Generates beat patterns based on audio and constraints."""

    PATTERN_TYPES = ["circle", "stream", "burst", "jump", "slider"]

    def generate(
        self,
        beat_idx: int,
        beat_time: float,
        section: dict,
        cursor_state: CursorMomentum,
        difficulty_params: dict,
        pattern_memory,
        mapping_style: MappingStyleEnum,
    ) -> str:
        """Generate pattern type for a beat.

        Args:
            beat_idx: Index of beat
            beat_time: Time of beat in seconds
            section: Current section info
            cursor_state: Current cursor state
            difficulty_params: Difficulty parameters
            pattern_memory: Pattern memory for avoiding repetition
            mapping_style: Mapping style

        Returns:
            Pattern type (circle, stream, burst, jump, slider)
        """
        # Determine pattern type based on:
        # 1. Section type
        # 2. Difficulty parameters
        # 3. Recent pattern history
        # 4. Mapping style weights

        section_type = section.get("type", "other")

        # Base probabilities by section
        section_probs = {
            "intro": {"circle": 0.6, "burst": 0.3, "stream": 0.1},
            "verse": {"circle": 0.4, "burst": 0.3, "stream": 0.2, "jump": 0.1},
            "build": {"circle": 0.2, "burst": 0.3, "stream": 0.3, "jump": 0.2},
            "drop": {"circle": 0.1, "burst": 0.2, "stream": 0.4, "jump": 0.3},
            "break": {"circle": 0.5, "slider": 0.5},
            "outro": {"circle": 0.7, "slider": 0.3},
        }

        probs = section_probs.get(section_type, section_probs["verse"])

        # Apply style weights
        style_weights = {
            MappingStyleEnum.TECHNICAL_STREAM: {"stream": 2.0},
            MappingStyleEnum.JUMP: {"jump": 2.0},
            MappingStyleEnum.AIM: {"jump": 1.8},
        }

        if mapping_style in style_weights:
            for pattern, weight in style_weights[mapping_style].items():
                if pattern in probs:
                    probs[pattern] *= weight

        # Normalize probabilities
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}

        # Avoid repetition
        recent_patterns = pattern_memory.get_recent(5)
        if recent_patterns:
            most_common = max(set(recent_patterns), key=recent_patterns.count)
            probs[most_common] *= 0.7  # Reduce probability of recent pattern

        # Renormalize
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}

        # Select pattern
        pattern_type = random.choices(
            list(probs.keys()),
            weights=list(probs.values()),
            k=1,
        )[0]

        return pattern_type
