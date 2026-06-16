"""Orchestrates complete beatmap generation pipeline."""

import logging
from uuid import UUID

from app.audio.analyzer import AudioAnalyzer
from app.mapping.engine import MappingEngine
from app.osu.osu_file_writer import OSUFileWriter
from app.osu.osz_packager import OSZPackager
from app.models.enums import DifficultyEnum, MappingStyleEnum

logger = logging.getLogger(__name__)


class GenerationService:
    """Orchestrates complete generation pipeline."""

    def __init__(self):
        """Initialize generation service."""
        self.audio_analyzer = AudioAnalyzer()
        self.mapping_engine = MappingEngine()
        self.osu_writer = OSUFileWriter()
        self.osz_packager = OSZPackager()

    def generate_beatmap(
        self,
        song_id: UUID,
        audio_file_path: str,
        difficulty: DifficultyEnum,
        mapping_style: MappingStyleEnum,
        target_star_rating: float,
        output_dir: str,
    ) -> dict:
        """Generate complete beatmap from audio file.

        Args:
            song_id: ID of uploaded song
            audio_file_path: Path to audio file
            difficulty: Difficulty level
            mapping_style: Mapping style
            target_star_rating: Target difficulty in stars
            output_dir: Output directory for files

        Returns:
            Dictionary with generation results
        """
        logger.info(
            f"Generating beatmap: song_id={song_id}, difficulty={difficulty}, style={mapping_style}"
        )

        try:
            # Step 1: Analyze audio
            logger.info("Step 1/4: Analyzing audio...")
            audio_features = self.audio_analyzer.analyze(audio_file_path)

            # Step 2: Generate beatmap
            logger.info("Step 2/4: Generating beatmap...")
            beatmap = self.mapping_engine.generate(
                audio_features=audio_features,
                difficulty=difficulty,
                mapping_style=mapping_style,
            )

            # Step 3: Write OSU file
            logger.info("Step 3/4: Writing OSU file...")
            osu_path = f"{output_dir}/{song_id}.osu"
            self.osu_writer.write(
                beatmap=beatmap,
                output_path=osu_path,
                title="Generated Beatmap",
                artist="Unknown",
            )

            # Step 4: Create OSZ package
            logger.info("Step 4/4: Creating OSZ package...")
            osz_path = f"{output_dir}/{song_id}.osz"
            self.osz_packager.package(
                osu_file_path=osu_path,
                audio_file_path=audio_file_path,
                output_path=osz_path,
            )

            result = {
                "song_id": str(song_id),
                "osu_file_path": osu_path,
                "osz_file_path": osz_path,
                "beatmap_metadata": {
                    "bpm": beatmap.bpm,
                    "drain_time": beatmap.drain_time,
                    "total_time": beatmap.total_time,
                    "object_count": len(beatmap.hit_objects),
                },
            }

            logger.info(f"Beatmap generation completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Beatmap generation failed: {str(e)}", exc_info=e)
            raise
