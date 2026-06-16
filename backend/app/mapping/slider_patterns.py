"""Advanced slider pattern generation with Bezier curves."""

import numpy as np
from typing import List, Tuple
from enum import Enum


class BezierCurve:
    """Generate smooth Bezier curves for slider paths."""

    @staticmethod
    def quadratic(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], t: float) -> Tuple[float, float]:
        """Compute quadratic Bezier curve point.
        
        Args:
            p0, p1, p2: Control points
            t: Parameter [0, 1]
            
        Returns:
            Point on curve (x, y)
        """
        x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
        y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
        return (x, y)

    @staticmethod
    def cubic(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], t: float) -> Tuple[float, float]:
        """Compute cubic Bezier curve point."""
        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    @staticmethod
    def catmull_rom(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], t: float) -> Tuple[float, float]:
        """Catmull-Rom spline (smooth through p1 and p2)."""
        t2 = t * t
        t3 = t2 * t
        
        x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
        y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
        
        return (x, y)

    @staticmethod
    def arc_length_parametrize(curve_func, p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], num_samples: int = 100) -> List[Tuple[float, float]]:
        """Parametrize curve by arc length for uniform sampling."""
        # Sample curve
        points = []
        distances = [0]
        total_distance = 0
        
        for i in range(num_samples + 1):
            t = i / num_samples
            point = curve_func(p0, p1, p2, t)
            points.append(point)
            
            if i > 0:
                dx = point[0] - points[i-1][0]
                dy = point[1] - points[i-1][1]
                dist = np.sqrt(dx**2 + dy**2)
                total_distance += dist
                distances.append(total_distance)
        
        # Uniform arc length samples
        result = []
        target_distances = np.linspace(0, total_distance, num_samples)
        
        for target in target_distances:
            idx = np.searchsorted(distances, target)
            idx = min(idx, len(points) - 1)
            result.append(points[idx])
        
        return result


class SliderPattern:
    """Generate slider patterns with various curves."""

    @staticmethod
    def linear_slider(start: Tuple[float, float], end: Tuple[float, float], num_ticks: int = 4) -> str:
        """Create linear slider path.
        
        Returns osu! slider path string (e.g., "L|100:100")
        """
        return f"L|{int(end[0])}:{int(end[1])}"

    @staticmethod
    def curved_slider(start: Tuple[float, float], control: Tuple[float, float], end: Tuple[float, float], num_ticks: int = 4) -> str:
        """Create curved slider using Bezier.
        
        Returns osu! slider path string (e.g., "B|100:100|200:150")
        """
        return f"B|{int(control[0])}:{int(control[1])}|{int(end[0])}:{int(end[1])}"

    @staticmethod
    def perfect_curve(start: Tuple[float, float], mid: Tuple[float, float], end: Tuple[float, float]) -> str:
        """Create perfect circle arc slider.
        
        Returns osu! slider path string (e.g., "P|100:100|200:150")
        """
        return f"P|{int(mid[0])}:{int(mid[1])}|{int(end[0])}:{int(end[1])}"

    @staticmethod
    def wave_slider(start: Tuple[float, float], direction: float, amplitude: float = 50, wavelength: float = 100) -> str:
        """Create wave/zigzag slider.
        
        Args:
            start: Starting position
            direction: Angle in radians
            amplitude: Wave height
            wavelength: Distance per wave cycle
        """
        end_x = start[0] + wavelength * np.cos(direction)
        end_y = start[1] + wavelength * np.sin(direction)
        
        # Control point perpendicular to direction
        perp_x = start[0] - amplitude * np.sin(direction)
        perp_y = start[1] + amplitude * np.cos(direction)
        
        return f"B|{int(perp_x)}:{int(perp_y)}|{int(end_x)}:{int(end_y)}"

    @staticmethod
    def spiral_slider(start: Tuple[float, float], num_rotations: int = 1.5, radius: float = 80) -> str:
        """Create spiral slider."""
        # Approximate spiral with multiple curve segments
        end_angle = num_rotations * 2 * np.pi
        control_angle = end_angle / 2
        
        control_x = start[0] + radius * np.cos(control_angle)
        control_y = start[1] + radius * np.sin(control_angle)
        
        end_x = start[0] + radius * np.cos(end_angle)
        end_y = start[1] + radius * np.sin(end_angle)
        
        return f"B|{int(control_x)}:{int(control_y)}|{int(end_x)}:{int(end_y)}"
