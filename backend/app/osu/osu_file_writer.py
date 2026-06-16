"""OSU file generation and writing."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class OSUFileWriter:
    """Writes generated beatmaps to .osu file format."""

    def write(
        self,
        beatmap,
        output_path: str,
        title: str = "Generated Beatmap",
        artist: str = "Unknown",
        audio_filename: str = "audio.mp3",
    ) -> str:
        """Write beatmap to .osu file.

        Args:
            beatmap: Generated beatmap object
            output_path: Output file path
            title: Beatmap title
            artist: Artist name
            audio_filename: Audio file name

        Returns:
            Path to created .osu file
        """
        logger.info(f"Writing OSU file: {output_path}")

        content = self._build_osu_content(
            beatmap=beatmap,
            title=title,
            artist=artist,
            audio_filename=audio_filename,
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"OSU file written: {output_path}")
        return output_path

    def _build_osu_content(self, beatmap, title: str, artist: str, audio_filename: str) -> str:
        """Build complete OSU file content."""
        lines = []

        # Format version
        lines.append("osu file format v14")
        lines.append("")

        # General section
        lines.append("[General]")
        lines.append(f"AudioFilename: {audio_filename}")
        lines.append(f"AudioLeadIn: 0")
        lines.append(f"PreviewTime: {int(beatmap.total_time * 1000 / 2)}")
        lines.append("Countdown: 0")
        lines.append("SampleSet: Soft")
        lines.append("StackLeniency: 0.7")
        lines.append("Mode: 0")
        lines.append("LetterboxInBreaks: 0")
        lines.append("WidescreenStoryboard: 0")
        lines.append("")

        # Editor section
        lines.append("[Editor]")
        lines.append("Bookmarks: ")
        lines.append("DistanceSpacing: 1")
        lines.append("BeatDivisor: 4")
        lines.append("GridSize: 4")
        lines.append("TimelineZoom: 2")
        lines.append("")

        # Metadata section
        lines.append("[Metadata]")
        lines.append(f"Title: {title}")
        lines.append(f"TitleUnicode: {title}")
        lines.append(f"Artist: {artist}")
        lines.append(f"ArtistUnicode: {artist}")
        lines.append("Creator: BeatForge")
        lines.append(f"Version: [BeatForge] Generated")
        lines.append("Source: BeatForge")
        lines.append("Tags: generated ai")
        lines.append("BeatmapID: 0")
        lines.append("BeatmapSetID: -1")
        lines.append("")

        # Difficulty section
        lines.append("[Difficulty]")
        lines.append("HPDrainRate: 7")
        lines.append("CircleSize: 4")
        lines.append("OverallDifficulty: 6")
        lines.append("ApproachRate: 8")
        lines.append(f"SliderMultiplier: {beatmap.bpm / 100}")
        lines.append("SliderTickRate: 1")
        lines.append("")

        # Events section (empty for now)
        lines.append("[Events]")
        lines.append("//Background and video events")
        lines.append("//Break Periods")
        lines.append("//Storyboard Layer 0 (Background)")
        lines.append("//Storyboard Layer 1 (Fail)")
        lines.append("//Storyboard Layer 2 (Pass)")
        lines.append("//Storyboard Layer 3 (Foreground)")
        lines.append("//Storyboard Layer 4 (Overlay)")
        lines.append("//Storyboard Sound Samples collection")
        lines.append("")

        # Timing Points section
        lines.append("[TimingPoints]")
        for timing_point in beatmap.timing_points:
            lines.append(
                f"{timing_point['time']},{timing_point['beat_duration']},"
                f"{timing_point['time_signature']},{timing_point['sample_set']},"
                f"{timing_point['sample_index']},{timing_point['volume']},"
                f"{1 if timing_point['inherited'] else 0},"
                f"{1 if timing_point['kiai_time'] else 0}"
            )
        lines.append("")

        # Hit Objects section
        lines.append("[HitObjects]")
        for obj in beatmap.hit_objects:
            lines.append(
                f"{obj['x']},{obj['y']},{obj['time']},1,0,0:0:0:0:"
            )
        lines.append("")

        return "\n".join(lines)
