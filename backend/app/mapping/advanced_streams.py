"""Advanced stream and complex pattern generation."""

import numpy as np
from typing import List, Tuple, Dict
from enum import Enum
from app.config import settings


class StreamType(Enum):
    """Types of advanced streams."""
    REGULAR_STREAM = "regular_stream"
    VIBRO_STREAM = "vibro_stream"  # Rapid back-and-forth
    TECHNICAL_STREAM = "technical_stream"  # Complex angles
    CUT_STREAM = "cut_stream"  # Curves at angles
    JUMP_STREAM = "jump_stream"  # Spaced out
    LONG_STREAM = "long_stream"  # Extended pattern


class AdvancedStreamGenerator:
    """Generate complex stream patterns with variations."""

    def __init__(self, playfield_width: int = settings.PLAYFIELD_WIDTH, playfield_height: int = settings.PLAYFIELD_HEIGHT):
        """Initialize stream generator."""
        self.width = playfield_width
        self.height = playfield_height

    def generate_regular_stream(
        self,
        start_pos: Tuple[float, float],
        direction: float,
        length: int = 8,
        spacing: float = 80.0,
    ) -> List[Tuple[float, float]]:
        """Generate regular alternating stream.
        
        Args:
            start_pos: Starting position
            direction: Initial direction in radians
            length: Number of notes
            spacing: Distance between notes
            
        Returns:
            List of positions
        """
        positions = [start_pos]
        current_angle = direction
        
        for i in range(1, length):
            # Alternate direction
            current_angle = direction + (np.pi if i % 2 == 1 else 0)
            
            x = positions[-1][0] + spacing * np.cos(current_angle)
            y = positions[-1][1] + spacing * np.sin(current_angle)
            
            # Constrain to playfield
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
        
        return positions

    def generate_vibro_stream(
        self,
        start_pos: Tuple[float, float],
        center_line: float,
        amplitude: float = 30.0,
        length: int = 16,
        spacing: float = 50.0,
    ) -> List[Tuple[float, float]]:
        """Generate vibro stream (tight back-and-forth oscillation).
        
        Args:
            start_pos: Starting position
            center_line: Angle of center line
            amplitude: Distance from center
            length: Number of notes
            spacing: Distance along center line
        """
        positions = []
        
        for i in range(length):
            # Along center line
            base_x = start_pos[0] + (i * spacing) * np.cos(center_line)
            base_y = start_pos[1] + (i * spacing) * np.sin(center_line)
            
            # Perpendicular oscillation
            perpendicular_angle = center_line + np.pi / 2
            oscillation = amplitude * ((-1) ** i)
            
            x = base_x + oscillation * np.cos(perpendicular_angle)
            y = base_y + oscillation * np.sin(perpendicular_angle)
            
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
        
        return positions

    def generate_technical_stream(
        self,
        start_pos: Tuple[float, float],
        angles: List[float],
        spacing: float = 80.0,
    ) -> List[Tuple[float, float]]:
        """Generate technical stream with varying angles.
        
        Args:
            start_pos: Starting position
            angles: List of angles for each note
            spacing: Distance between notes
        """
        positions = [start_pos]
        
        for angle in angles:
            x = positions[-1][0] + spacing * np.cos(angle)
            y = positions[-1][1] + spacing * np.sin(angle)
            
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
        
        return positions

    def generate_cut_stream(
        self,
        start_pos: Tuple[float, float],
        primary_angle: float,
        cut_angle: float,
        length: int = 8,
        spacing: float = 80.0,
    ) -> List[Tuple[float, float]]:
        """Generate cut stream (diagonal cuts across main pattern).
        
        Args:
            start_pos: Starting position
            primary_angle: Main direction
            cut_angle: Cutting direction (usually perpendicular)
            length: Number of notes
            spacing: Distance between notes
        """
        positions = []
        
        for i in range(length):
            # Alternate between primary and cut directions
            angle = primary_angle if i % 2 == 0 else cut_angle
            
            if i == 0:
                x, y = start_pos
            else:
                x = positions[-1][0] + spacing * np.cos(angle)
                y = positions[-1][1] + spacing * np.sin(angle)
            
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
        
        return positions

    def generate_jump_stream(
        self,
        start_pos: Tuple[float, float],
        direction: float,
        length: int = 6,
        jump_distance: float = 150.0,
    ) -> List[Tuple[float, float]]:
        """Generate jump stream (spaced out pattern)."""
        positions = [start_pos]
        
        for i in range(1, length):
            angle = direction + (np.pi if i % 2 == 1 else 0)
            
            x = positions[-1][0] + jump_distance * np.cos(angle)
            y = positions[-1][1] + jump_distance * np.sin(angle)
            
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
        
        return positions

    def generate_long_stream(
        self,
        start_pos: Tuple[float, float],
        direction: float,
        length: int = 20,
        spacing: float = 60.0,
        spacing_acceleration: float = 1.0,
    ) -> List[Tuple[float, float]]:
        """Generate long extended stream with optional acceleration.
        
        Args:
            start_pos: Starting position
            direction: Initial direction
            length: Number of notes
            spacing: Initial spacing
            spacing_acceleration: Multiplier for spacing increase
        """
        positions = [start_pos]
        current_spacing = spacing
        
        for i in range(1, length):
            angle = direction + (np.pi if i % 2 == 1 else 0)
            
            x = positions[-1][0] + current_spacing * np.cos(angle)
            y = positions[-1][1] + current_spacing * np.sin(angle)
            
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
            
            # Gradually increase spacing
            current_spacing *= spacing_acceleration
        
        return positions

    def generate_antistream(
        self,
        start_pos: Tuple[float, float],
        length: int = 8,
        spacing: float = 80.0,
    ) -> List[Tuple[float, float]]:
        """Generate anti-stream (sharp angle changes)."""
        positions = [start_pos]
        angles = np.linspace(0, 2 * np.pi, length)
        
        for angle in angles[1:]:
            x = start_pos[0] + spacing * np.cos(angle)
            y = start_pos[1] + spacing * np.sin(angle)
            
            x = np.clip(x, 0, self.width)
            y = np.clip(y, 0, self.height)
            
            positions.append((x, y))
        
        return positions
