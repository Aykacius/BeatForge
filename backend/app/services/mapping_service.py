"""Beatmap mapping service orchestrator."""

from loguru import logger
from app.audio.analyzer import AudioAnalyzer
from app.mapping.engine import MappingEngine
from app.osu.writer import OsuWriter


class MappingService:
    """Orchestrates the complete mapping pipeline."""

    def __init__(self):
        """Initialize mapping service."""
        self.audio_analyzer = AudioAnalyzer()
        self.mapping_engine = MappingEngine()
        self.osu_writer = OsuWriter()

    async def generate_beatmap(
        self,
        file_path: str,
        difficulty: str,
        mapping_style: str,
        target_star_rating: float,
    ) -> dict:
        """Generate a beatmap from an audio file.
        
        Args:
            file_path: Path to MP3 file
            difficulty: Difficulty level
            mapping_style: Mapping style preference
            target_star_rating: Target star rating
            
        Returns:
            Dictionary with beatmap paths and metadata
        """
        logger.info(f"Starting beatmap generation for {file_path}")

        try:
            # Step 1: Analyze audio
            logger.info("Step 1: Analyzing audio...")
            audio_analysis = await self.audio_analyzer.analyze(file_path)
            logger.info(f"  BPM: {audio_analysis['bpm']}")
            logger.info(f"  Duration: {audio_analysis['duration']}s")

            # Step 2: Generate mapping
            logger.info("Step 2: Generating mapping...")
            hit_objects = await self.mapping_engine.generate(
                audio_analysis=audio_analysis,
                difficulty=difficulty,
                mapping_style=mapping_style,
                target_star_rating=target_star_rating,
            )
            logger.info(f"  Generated {len(hit_objects)} hit objects")

            # Step 3: Write .osu file
            logger.info("Step 3: Writing .osu file...")
            osu_file = await self.osu_writer.write(
                audio_analysis=audio_analysis,
                hit_objects=hit_objects,
                difficulty=difficulty,
            )
            logger.info(f"  Written to {osu_file}")

            return {
                "osu_file": osu_file,
                "audio_analysis": audio_analysis,
                "hit_objects_count": len(hit_objects),
            }

        except Exception as e:
            logger.error(f"Beatmap generation failed: {str(e)}")
            raise
