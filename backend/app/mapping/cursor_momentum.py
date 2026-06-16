"""Cursor momentum and state tracking."""

import logging
from dataclasses import dataclass, field
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CursorState:
    """Represents cursor state and momentum."""

    position: Tuple[float, float] = (256, 192)  # Center of playfield
    velocity: float = 0.0
    direction: float = 0.0  # In radians
    angle_memory: float = 0.0  # Weighted historical angle
    last_update_time: float = 0.0
    
    # Momentum parameters
    momentum_factor: float = 0.7  # How much previous direction influences next
    velocity_decay: float = 0.9  # How quickly velocity decays


class CursorMomentum:
    """Manages cursor state and momentum for flow preservation."""

    def __init__(self, playfield_width: int = 512, playfield_height: int = 384):
        """Initialize cursor momentum tracker.

        Args:
            playfield_width: osu! playfield width in pixels
            playfield_height: osu! playfield height in pixels
        """
        self.playfield_width = playfield_width
        self.playfield_height = playfield_height
        self.state = CursorState()
        self.history = []

    def reset(self):
        """Reset cursor to center position."""
        self.state = CursorState(position=(self.playfield_width / 2, self.playfield_height / 2))
        self.history = []
        logger.info("Cursor momentum reset")

    def update_position(
        self,
        new_position: Tuple[float, float],
        time_delta: float = 0.1,
    ) -> CursorState:
        """Update cursor position while preserving momentum.

        Args:
            new_position: Target position (x, y)
            time_delta: Time since last update

        Returns:
            Updated cursor state
        """
        # Calculate movement
        dx = new_position[0] - self.state.position[0]
        dy = new_position[1] - self.state.position[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Update velocity
        self.state.velocity = distance / (time_delta + 1e-6)
        self.state.velocity *= self.state.velocity_decay

        # Update direction
        if distance > 0:
            new_direction = np.arctan2(dy, dx)
            self.state.direction = (
                self.state.momentum_factor * self.state.angle_memory
                + (1 - self.state.momentum_factor) * new_direction
            )
            self.state.angle_memory = self.state.direction

        # Update position
        self.state.position = (
            np.clip(new_position[0], 0, self.playfield_width),
            np.clip(new_position[1], 0, self.playfield_height),
        )
        self.state.last_update_time += time_delta

        # Record in history
        self.history.append(
            {
                "time": self.state.last_update_time,
                "position": self.state.position,
                "direction": self.state.direction,
            }
        )

        return self.state

    def get_next_position(
        self,
        max_distance: float,
        angle_preference: float = None,
    ) -> Tuple[float, float]:
        """Get next cursor position based on momentum and constraints.

        Args:
            max_distance: Maximum distance cursor can travel (based on difficulty)
            angle_preference: Preferred angle if any

        Returns:
            Suggested next position (x, y)
        """
        if angle_preference is None:
            angle = self.state.direction
        else:
            # Blend preferred angle with current momentum
            angle = (
                0.6 * self.state.direction + 0.4 * angle_preference
            )

        # Calculate new position
        x = self.state.position[0] + max_distance * np.cos(angle)
        y = self.state.position[1] + max_distance * np.sin(angle)

        # Clamp to playfield
        x = np.clip(x, 0, self.playfield_width)
        y = np.clip(y, 0, self.playfield_height)

        return (x, y)
