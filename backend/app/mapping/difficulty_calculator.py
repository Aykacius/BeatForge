"""Star rating and difficulty calculation."""

import numpy as np
from typing import List, Dict

from app.mapping.engine import HitObject


class DifficultyCalculator:
    """Calculate difficulty metrics for generated beatmaps."""

    def calculate(
        self,
        hit_objects: List[HitObject],
        bpm: float,
    ) -> Dict:
        """Calculate beatmap difficulty metrics.
        
        Args:
            hit_objects: List of hit objects
            bpm: Song BPM
            
        Returns:
            Dictionary with difficulty metrics
        """
        if len(hit_objects) < 2:
            return {"star_rating": 0.0, "aim_difficulty": 0.0, "speed_difficulty": 0.0}

        # Calculate spacing
        spacings = []
        for i in range(len(hit_objects) - 1):
            obj1 = hit_objects[i]
            obj2 = hit_objects[i + 1]
            
            dx = obj2.x - obj1.x
            dy = obj2.y - obj1.y
            distance = np.sqrt(dx**2 + dy**2)
            time_delta = (obj2.time - obj1.time) / 1000.0  # Convert to seconds
            
            if time_delta > 0:
                spacings.append({
                    "distance": distance,
                    "time_delta": time_delta,
                    "speed": distance / time_delta,
                })

        # Calculate aim difficulty (based on spacing and angles)
        aim_difficulty = self._calculate_aim(spacings)
        
        # Calculate speed difficulty (based on timing)
        speed_difficulty = self._calculate_speed(spacings, bpm)
        
        # Combine to get star rating
        star_rating = np.sqrt(aim_difficulty**2 + speed_difficulty**2) / 10.0
        
        return {
            "star_rating": min(10.0, star_rating),
            "aim_difficulty": aim_difficulty,
            "speed_difficulty": speed_difficulty,
            "avg_spacing": np.mean([s["distance"] for s in spacings]),
            "max_spacing": max([s["distance"] for s in spacings]),
        }

    def _calculate_aim(self, spacings: List[Dict]) -> float:
        """Calculate aim-based difficulty."""
        if not spacings:
            return 0.0
        
        avg_spacing = np.mean([s["distance"] for s in spacings])
        max_spacing = max([s["distance"] for s in spacings])
        
        # Normalize to 0-10 scale
        return (avg_spacing + max_spacing) / 50.0

    def _calculate_speed(self, spacings: List[Dict], bpm: float) -> float:
        """Calculate speed-based difficulty."""
        if not spacings:
            return 0.0
        
        speeds = [s["speed"] for s in spacings]
        avg_speed = np.mean(speeds)
        max_speed = max(speeds)
        
        # Normalize to 0-10 scale
        return (avg_speed + max_speed) / 100.0
