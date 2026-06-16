"""Pattern generation grammar and templates."""

import numpy as np
from typing import List, Tuple, Dict
from enum import Enum


class PatternType(Enum):
    """Types of patterns the grammar can generate."""
    CIRCLE = "circle"
    STREAM = "stream"
    BURST = "burst"
    JUMP_STREAM = "jump_stream"
    CUT_STREAM = "cut_stream"
    WIGGLE = "wiggle"
    TRIANGLE = "triangle"
    SQUARE = "square"
    ARC = "arc"
    SLIDER = "slider"
    ACCELERATING_STREAM = "accelerating_stream"


class PatternGrammar:
    """Generates hit object patterns using a grammar system."""

    def __init__(self):
        """Initialize pattern grammar."""
        self.pattern_memory: List[str] = []  # Prevent repetition
        self.max_memory = 5

    def generate(
        self,
        pattern_type: str,
        config: Dict,
    ) -> List[Tuple[float, float]]:
        """Generate positions for a pattern.
        
        Args:
            pattern_type: Type of pattern to generate
            config: Difficulty configuration
            
        Returns:
            List of (x, y) positions
        """
        # Avoid repetition
        if len(self.pattern_memory) >= self.max_memory:
            self.pattern_memory.pop(0)

        if pattern_type == "circle":
            positions = self._generate_circle(config)
        elif pattern_type == "stream":
            positions = self._generate_stream(config)
        elif pattern_type == "burst":
            positions = self._generate_burst(config)
        elif pattern_type == "jump":
            positions = self._generate_jump(config)
        elif pattern_type == "wiggle":
            positions = self._generate_wiggle(config)
        elif pattern_type == "triangle":
            positions = self._generate_triangle(config)
        elif pattern_type == "accelerating_stream":
            positions = self._generate_accelerating_stream(config)
        else:
            positions = self._generate_circle(config)

        self.pattern_memory.append(pattern_type)
        return positions

    def _generate_circle(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate single circle position."""
        return [(256.0, 192.0)]  # Center of playfield

    def _generate_stream(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate stream pattern (rapid circles in alternating pattern)."""
        positions = []
        stream_length = config.get("stream_length", 5)
        spacing = config.get("min_spacing", 80.0)
        
        angle = 0
        for i in range(stream_length):
            x = 256.0 + spacing * np.cos(angle)
            y = 192.0 + spacing * np.sin(angle)
            positions.append((x, y))
            angle += np.pi  # Alternate sides
        
        return positions

    def _generate_burst(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate burst pattern (3-4 quick circles)."""
        positions = []
        spacing = config.get("min_spacing", 80.0) * 0.8
        
        for i in range(3):
            angle = (i / 3) * 2 * np.pi
            x = 256.0 + spacing * np.cos(angle)
            y = 192.0 + spacing * np.sin(angle)
            positions.append((x, y))
        
        return positions

    def _generate_jump(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate jump pattern (2 distant circles)."""
        jump_distance = config.get("jump_distance", 150.0)
        angle = np.random.uniform(0, 2 * np.pi)
        
        pos1 = (256.0 + jump_distance * np.cos(angle), 192.0 + jump_distance * np.sin(angle))
        pos2 = (256.0 - jump_distance * np.cos(angle), 192.0 - jump_distance * np.sin(angle))
        
        return [pos1, pos2]

    def _generate_wiggle(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate wiggle pattern (curved alternating path)."""
        positions = []
        spacing = config.get("min_spacing", 80.0) * 0.6
        
        for i in range(4):
            x_offset = spacing * ((-1) ** i)
            y_offset = spacing * 0.5 * i
            positions.append((256.0 + x_offset, 192.0 + y_offset))
        
        return positions

    def _generate_triangle(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate triangle pattern."""
        spacing = config.get("max_spacing", 200.0) * 0.7
        
        return [
            (256.0, 192.0 - spacing),
            (256.0 - spacing, 192.0 + spacing),
            (256.0 + spacing, 192.0 + spacing),
        ]

    def _generate_accelerating_stream(self, config: Dict) -> List[Tuple[float, float]]:
        """Generate stream that accelerates."""
        positions = []
        spacing_start = config.get("min_spacing", 80.0)
        spacing_end = config.get("max_spacing", 200.0)
        stream_length = config.get("stream_length", 8)
        
        for i in range(stream_length):
            ratio = i / stream_length
            spacing = spacing_start + (spacing_end - spacing_start) * ratio
            angle = (i % 2) * np.pi
            
            x = 256.0 + spacing * np.cos(angle)
            y = 192.0 + spacing * np.sin(angle)
            positions.append((x, y))
        
        return positions
