"""Maps audio events to pattern types."""

import logging

logger = logging.getLogger(__name__)


class MusicalMapper:
    """Maps musical events (kicks, snares, vocals) to pattern types."""

    def map_kick(self) -> str:
        """Map kick drum to pattern."""
        return "circle"

    def map_snare(self) -> str:
        """Map snare to pattern."""
        return "burst"

    def map_vocal(self) -> str:
        """Map vocal peak to pattern."""
        return "slider"

    def map_drop(self) -> str:
        """Map drop section to pattern."""
        return "stream"

    def map_quiet_section(self) -> str:
        """Map quiet section to pattern."""
        return "circle"
