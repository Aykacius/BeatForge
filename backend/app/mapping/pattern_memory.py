"""Pattern history and repetition avoidance."""

import logging
from collections import deque

logger = logging.getLogger(__name__)


class PatternMemory:
    """Tracks recent patterns to avoid excessive repetition."""

    def __init__(self, max_history: int = 20):
        """Initialize pattern memory.

        Args:
            max_history: Maximum number of patterns to remember
        """
        self.max_history = max_history
        self.history = deque(maxlen=max_history)

    def add(self, pattern_type: str):
        """Add pattern to history.

        Args:
            pattern_type: Type of pattern
        """
        self.history.append(pattern_type)

    def get_recent(self, count: int = 5) -> list[str]:
        """Get recent patterns.

        Args:
            count: Number of recent patterns to return

        Returns:
            List of recent pattern types
        """
        return list(self.history)[-count:]

    def get_frequency(self) -> dict[str, float]:
        """Get frequency of each pattern type.

        Returns:
            Dictionary with pattern types and their frequencies
        """
        if not self.history:
            return {}

        frequencies = {}
        for pattern in self.history:
            frequencies[pattern] = frequencies.get(pattern, 0) + 1

        total = sum(frequencies.values())
        return {k: v / total for k, v in frequencies.items()}

    def clear(self):
        """Clear pattern history."""
        self.history.clear()
