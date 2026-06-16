"""Cursor momentum and physics simulation."""

import numpy as np
from typing import Tuple
from loguru import logger


class CursorPhysics:
    """Simulates osu! cursor movement with momentum and inertia."""

    def __init__(
        self,
        min_distance: float,
        max_distance: float,
        playfield_width: int,
        playfield_height: int,
    ):
        """Initialize cursor physics.
        
        Args:
            min_distance: Minimum distance between objects
            max_distance: Maximum distance between objects
            playfield_width: Playfield width
            playfield_height: Playfield height
        """
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.playfield_width = playfield_width
        self.playfield_height = playfield_height
        self.friction = 0.95  # Velocity decay
        self.max_velocity = 500.0  # pixels per second

    def apply(
        self,
        current_pos: Tuple[float, float],
        target_pos: Tuple[float, float],
        current_velocity: np.ndarray,
        current_direction: float,
        time_since_last: float,
    ) -> Tuple[float, float, np.ndarray, float]:
        """Apply physics to cursor movement.
        
        Args:
            current_pos: Current cursor position
            target_pos: Target position to reach
            current_velocity: Current velocity vector
            current_direction: Current angle in radians
            time_since_last: Time since last update
            
        Returns:
            Tuple of (new_x, new_y, new_velocity, new_direction)
        """
        current_x, current_y = current_pos
        target_x, target_y = target_pos

        # Calculate direction to target
        dx = target_x - current_x
        dy = target_y - current_y
        distance = np.sqrt(dx**2 + dy**2)

        if distance < 0.01:
            # Already at target
            new_velocity = current_velocity * self.friction
            return current_x, current_y, new_velocity, current_direction

        # Normalize direction
        dir_x = dx / distance
        dir_y = dy / distance
        target_direction = np.arctan2(dy, dx)

        # Smooth direction change (cursor can't turn instantly)
        direction_diff = self._normalize_angle(target_direction - current_direction)
        max_turn_rate = 0.3  # radians per update
        direction_change = np.clip(direction_diff, -max_turn_rate, max_turn_rate)
        new_direction = current_direction + direction_change

        # Accelerate toward target
        desired_speed = min(self.max_velocity, distance * 2)
        current_speed = np.linalg.norm(current_velocity)
        
        if current_speed < desired_speed:
            acceleration = 300.0  # pixels per second^2
            speed_delta = acceleration * time_since_last
            new_speed = min(current_speed + speed_delta, desired_speed)
        else:
            new_speed = current_speed * self.friction

        # Apply friction
        new_velocity = np.array([
            np.cos(new_direction) * new_speed,
            np.sin(new_direction) * new_speed,
        ])

        # Update position
        new_x = current_x + new_velocity[0] * time_since_last
        new_y = current_y + new_velocity[1] * time_since_last

        # Constrain to playfield
        new_x = np.clip(new_x, 0, self.playfield_width)
        new_y = np.clip(new_y, 0, self.playfield_height)

        return new_x, new_y, new_velocity, new_direction

    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-pi, pi]."""
        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi
        return angle
