"""Difficulty parameter management."""

import logging

from app.models.enums import DifficultyEnum, MappingStyleEnum

logger = logging.getLogger(__name__)


class DifficultyManager:
    """Maps difficulty levels to generation parameters."""

    # Difficulty parameters
    DIFFICULTY_PARAMS = {
        DifficultyEnum.EASY: {
            "spacing": (80, 120),  # Min-max pixel spacing
            "object_density": (1.5, 2.5),  # Objects per second
            "max_stream_length": 3,
            "jump_distance": (50, 100),
            "slider_ratio": 0.4,
            "spinner_count": 0,
        },
        DifficultyEnum.NORMAL: {
            "spacing": (120, 180),
            "object_density": (2.5, 3.5),
            "max_stream_length": 5,
            "jump_distance": (100, 150),
            "slider_ratio": 0.35,
            "spinner_count": 0,
        },
        DifficultyEnum.HARD: {
            "spacing": (180, 250),
            "object_density": (3.5, 4.5),
            "max_stream_length": 8,
            "jump_distance": (150, 220),
            "slider_ratio": 0.3,
            "spinner_count": 1,
        },
        DifficultyEnum.INSANE: {
            "spacing": (250, 350),
            "object_density": (4.5, 5.5),
            "max_stream_length": 12,
            "jump_distance": (220, 350),
            "slider_ratio": 0.25,
            "spinner_count": 2,
        },
        DifficultyEnum.EXPERT_PLUS: {
            "spacing": (350, 512),
            "object_density": (5.5, 7.0),
            "max_stream_length": 16,
            "jump_distance": (300, 400),
            "slider_ratio": 0.2,
            "spinner_count": 3,
        },
    }

    # Mapping style modifiers
    STYLE_MODIFIERS = {
        MappingStyleEnum.TECHNICAL_STREAM: {
            "stream_weight": 1.5,
            "jump_weight": 0.5,
            "spacing_multiplier": 0.9,
        },
        MappingStyleEnum.JUMP: {
            "stream_weight": 0.3,
            "jump_weight": 2.0,
            "spacing_multiplier": 1.3,
        },
        MappingStyleEnum.HYBRID: {
            "stream_weight": 1.0,
            "jump_weight": 1.0,
            "spacing_multiplier": 1.0,
        },
        MappingStyleEnum.AIM: {
            "stream_weight": 0.2,
            "jump_weight": 1.8,
            "spacing_multiplier": 1.4,
        },
        MappingStyleEnum.STREAM_PRACTICE: {
            "stream_weight": 2.0,
            "jump_weight": 0.2,
            "spacing_multiplier": 0.8,
        },
    }

    def get_parameters(
        self,
        difficulty: DifficultyEnum,
        mapping_style: MappingStyleEnum = MappingStyleEnum.HYBRID,
    ) -> dict:
        """Get generation parameters for given difficulty and style.

        Args:
            difficulty: Difficulty level
            mapping_style: Mapping style (optional)

        Returns:
            Dictionary with generation parameters
        """
        # Get base difficulty parameters
        base_params = self.DIFFICULTY_PARAMS.get(
            difficulty, self.DIFFICULTY_PARAMS[DifficultyEnum.NORMAL]
        )

        # Get style modifiers
        modifiers = self.STYLE_MODIFIERS.get(
            mapping_style, self.STYLE_MODIFIERS[MappingStyleEnum.HYBRID]
        )

        # Apply modifiers
        params = base_params.copy()
        spacing_min, spacing_max = params["spacing"]
        spacing_multiplier = modifiers["spacing_multiplier"]
        params["spacing"] = (
            int(spacing_min * spacing_multiplier),
            int(spacing_max * spacing_multiplier),
        )

        params["stream_weight"] = modifiers["stream_weight"]
        params["jump_weight"] = modifiers["jump_weight"]

        logger.info(
            f"Difficulty parameters: {difficulty} + {mapping_style} = {params}"
        )

        return params
