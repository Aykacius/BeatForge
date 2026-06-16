"""Core beatmap mapping engine with cursor momentum and pattern grammar."""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum
from loguru import logger

from app.config import settings
from app.audio.analyzer import AudioAnalysis
from app.mapping.cursor_physics import CursorPhysics
from app.mapping.pattern_grammar import PatternGrammar
from app.mapping.difficulty_calculator import DifficultyCalculator


class ObjectType(Enum):
    """osu! hit object types."""
    CIRCLE = 1
    SLIDER = 2
    SPINNER = 8


@dataclass
class HitObject:
    """Represents a single hit object in the beatmap."""
    x: float
    y: float
    time: float  # milliseconds
    object_type: ObjectType
    hit_sound: int
    slider_path: str = ""  # For sliders
    slider_duration: float = 0.0  # For sliders
    combo_number: int = 0
    new_combo: bool = False


class MappingEngine:
    """Main beatmap generation engine."""

    def __init__(self):
        """Initialize mapping engine."""
        self.cursor_physics = CursorPhysics(
            min_distance=settings.MIN_CIRCLE_DISTANCE,
            max_distance=settings.MAX_CIRCLE_DISTANCE,
            playfield_width=settings.PLAYFIELD_WIDTH,
            playfield_height=settings.PLAYFIELD_HEIGHT,
        )
        self.pattern_grammar = PatternGrammar()
        self.difficulty_calculator = DifficultyCalculator()
        self.playfield_width = settings.PLAYFIELD_WIDTH
        self.playfield_height = settings.PLAYFIELD_HEIGHT

    async def generate(
        self,
        audio_analysis: AudioAnalysis,
        difficulty: str,
        mapping_style: str,
        target_star_rating: float,
    ) -> List[HitObject]:
        """Generate beatmap from audio analysis.
        
        Args:
            audio_analysis: Results from audio analysis
            difficulty: Difficulty level
            mapping_style: Desired mapping style
            target_star_rating: Target star rating
            
        Returns:
            List of HitObject instances
        """
        logger.info(f"Generating beatmap: {difficulty} {mapping_style} {target_star_rating}★")

        # Configure for difficulty
        config = self._get_difficulty_config(difficulty, target_star_rating)
        logger.info(f"Difficulty config: {config}")

        # Initialize cursor
        cursor_x, cursor_y = self.playfield_width / 2, self.playfield_height / 2
        cursor_velocity = np.array([0.0, 0.0])
        cursor_direction = 0.0
        combo_counter = 0

        hit_objects: List[HitObject] = []

        # Iterate through onsets and beats
        for onset_time in audio_analysis.onset_times:
            if onset_time >= audio_analysis.duration:
                break

            # Find current section
            section = self._get_section_at_time(audio_analysis.sections, onset_time)
            
            # Find energy at this time
            energy = self._get_energy_at_time(audio_analysis.energy, audio_analysis.energy_times, onset_time)

            # Determine pattern type based on context
            pattern_type = self._determine_pattern_type(
                section=section,
                energy=energy,
                style=mapping_style,
                difficulty=difficulty,
            )

            logger.debug(f"Time {onset_time:.2f}s: {section['label']} - {pattern_type}")

            # Generate pattern
            pattern_positions = self.pattern_grammar.generate(
                pattern_type=pattern_type,
                config=config,
            )

            # Apply cursor physics to positions
            adjusted_positions = []
            for pos in pattern_positions:
                next_x, next_y, new_velocity, new_direction = self.cursor_physics.apply(
                    current_pos=(cursor_x, cursor_y),
                    target_pos=pos,
                    current_velocity=cursor_velocity,
                    current_direction=cursor_direction,
                    time_since_last=0.1,  # Approximate
                )
                adjusted_positions.append((next_x, next_y))
                cursor_x, cursor_y = next_x, next_y
                cursor_velocity = new_velocity
                cursor_direction = new_direction

            # Create hit objects
            start_time_ms = int(onset_time * 1000)
            for i, (x, y) in enumerate(adjusted_positions):
                obj = HitObject(
                    x=x,
                    y=y,
                    time=start_time_ms + i * 100,
                    object_type=ObjectType.CIRCLE,
                    hit_sound=0,
                    combo_number=combo_counter,
                    new_combo=(i == 0),
                )
                hit_objects.append(obj)
                combo_counter += 1

        logger.info(f"Generated {len(hit_objects)} hit objects")
        return hit_objects

    def _get_difficulty_config(self, difficulty: str, target_sr: float) -> Dict:
        """Get configuration parameters for difficulty level."""
        configs = {
            "Easy": {
                "min_spacing": 100.0,
                "max_spacing": 150.0,
                "object_density": 0.3,
                "stream_length": 3,
                "jump_distance": 80.0,
            },
            "Normal": {
                "min_spacing": 80.0,
                "max_spacing": 180.0,
                "object_density": 0.5,
                "stream_length": 5,
                "jump_distance": 120.0,
            },
            "Hard": {
                "min_spacing": 60.0,
                "max_spacing": 220.0,
                "object_density": 0.7,
                "stream_length": 8,
                "jump_distance": 150.0,
            },
            "Insane": {
                "min_spacing": 40.0,
                "max_spacing": 280.0,
                "object_density": 0.85,
                "stream_length": 12,
                "jump_distance": 200.0,
            },
            "Expert+": {
                "min_spacing": 30.0,
                "max_spacing": 300.0,
                "object_density": 0.95,
                "stream_length": 16,
                "jump_distance": 250.0,
            },
        }
        return configs.get(difficulty, configs["Normal"])

    def _get_section_at_time(self, sections: List[Dict], time: float) -> Dict:
        """Get section information at given time."""
        for section in sections:
            if section["start"] <= time < section["end"]:
                return section
        return sections[-1] if sections else {"label": "outro", "start": time, "end": time + 1}

    def _get_energy_at_time(self, energy: np.ndarray, times: np.ndarray, time: float) -> float:
        """Get energy level at given time."""
        idx = np.searchsorted(times, time)
        if idx >= len(energy):
            return energy[-1]
        return float(energy[idx])

    def _determine_pattern_type(self, section: Dict, energy: float, style: str, difficulty: str) -> str:
        """Determine what pattern type to generate."""
        # Simple heuristic based on section and energy
        if section["label"] == "drop" and energy > 0.6:
            if style == "Stream Practice":
                return "stream"
            elif style == "Jump":
                return "jump"
            else:
                return "burst"
        elif section["label"] == "build":
            return "accelerating_stream"
        else:
            return "circle" if energy < 0.3 else "burst"
