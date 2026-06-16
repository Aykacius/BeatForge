"""Main mapping engine orchestrator."""

import logging
from dataclasses import dataclass

import numpy as np

from app.mapping.cursor_momentum import CursorMomentum
from app.mapping.pattern_generator import PatternGenerator
from app.mapping.difficulty_manager import DifficultyManager
from app.mapping.pattern_memory import PatternMemory
from app.models.enums import DifficultyEnum, MappingStyleEnum
from app.utils.exceptions import MappingError

logger = logging.getLogger(__name__)


@dataclass
class GeneratedBeatmap:
    """Container for generated beatmap data."""

    hit_objects: list
    timing_points: list
    bpm: float
    drain_time: float
    total_time: float
    metadata: dict


class MappingEngine:
    """Orchestrates complete beatmap generation."""

    def __init__(self):
        """Initialize mapping engine."""
        self.cursor_momentum = CursorMomentum()
        self.pattern_generator = PatternGenerator()
        self.difficulty_manager = DifficultyManager()
        self.pattern_memory = PatternMemory()

    def generate(
        self,
        audio_features: dict,
        difficulty: DifficultyEnum,
        mapping_style: MappingStyleEnum,
    ) -> GeneratedBeatmap:
        """Generate complete beatmap from audio features.

        Args:
            audio_features: Analysis results from AudioAnalyzer
            difficulty: Target difficulty level
            mapping_style: Target mapping style

        Returns:
            GeneratedBeatmap with hit objects and metadata
        """
        logger.info(
            f"Starting beatmap generation: difficulty={difficulty}, style={mapping_style}"
        )

        try:
            # Get difficulty parameters
            params = self.difficulty_manager.get_parameters(
                difficulty=difficulty, mapping_style=mapping_style
            )
            logger.info(f"Difficulty parameters: {params}")

            # Initialize
            self.cursor_momentum.reset()
            self.pattern_memory.clear()

            hit_objects = []
            bpm = audio_features["bpm"]
            beats = np.array(audio_features["beats"])
            sections = audio_features["sections"]

            # Generate patterns for each beat
            for beat_idx, beat_time in enumerate(beats):
                # Find current section
                current_section = self._get_section_at_time(beat_time, sections)

                # Generate pattern
                pattern_type = self.pattern_generator.generate(
                    beat_idx=beat_idx,
                    beat_time=beat_time,
                    section=current_section,
                    cursor_state=self.cursor_momentum,
                    difficulty_params=params,
                    pattern_memory=self.pattern_memory,
                    mapping_style=mapping_style,
                )

                # Create hit object
                hit_object = self._create_hit_object(
                    pattern_type=pattern_type,
                    beat_time=beat_time,
                    cursor_state=self.cursor_momentum,
                    params=params,
                )

                hit_objects.append(hit_object)
                self.pattern_memory.add(pattern_type)

                if (beat_idx + 1) % 100 == 0:
                    logger.info(f"Generated {beat_idx + 1} objects...")

            logger.info(f"Total hit objects generated: {len(hit_objects)}")

            # Create timing points
            timing_points = self._create_timing_points(bpm, beats)

            # Create metadata
            metadata = {
                "creator": "BeatForge AI",
                "version": "[BeatForge] Generated",
                "drain_time": beats[-1],
                "total_time": audio_features["duration"],
            }

            result = GeneratedBeatmap(
                hit_objects=hit_objects,
                timing_points=timing_points,
                bpm=bpm,
                drain_time=beats[-1],
                total_time=audio_features["duration"],
                metadata=metadata,
            )

            logger.info("Beatmap generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Beatmap generation failed: {str(e)}")
            raise MappingError(f"Failed to generate beatmap: {str(e)}")

    def _get_section_at_time(self, time: float, sections: list[dict]) -> dict:
        """Get current section for a given time."""
        for section in sections:
            if section["start_time"] <= time < section["end_time"]:
                return section
        return sections[-1] if sections else {"type": "other"}

    def _create_hit_object(self, pattern_type: str, beat_time: float, cursor_state, params: dict):
        """Create a hit object from pattern type."""
        # Simplified hit object creation
        position = cursor_state.position
        return {
            "x": int(position[0]),
            "y": int(position[1]),
            "time": int(beat_time * 1000),
            "type": pattern_type,
        }

    def _create_timing_points(self, bpm: float, beats: np.ndarray) -> list[dict]:
        """Create timing points for the beatmap."""
        beat_duration = 60000 / bpm  # in milliseconds
        timing_points = []

        if len(beats) > 0:
            timing_points.append(
                {
                    "time": int(beats[0] * 1000),
                    "beat_duration": beat_duration,
                    "time_signature": 4,
                    "sample_set": 0,
                    "sample_index": 0,
                    "volume": 100,
                    "inherited": False,
                    "kiai_time": False,
                }
            )

        return timing_points
