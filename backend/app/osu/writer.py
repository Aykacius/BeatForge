"""Generate valid .osu beatmap files."""

import os
from typing import List, Dict
from loguru import logger

from app.config import settings
from app.audio.analyzer import AudioAnalysis
from app.mapping.engine import HitObject, ObjectType


class OsuWriter:
    """Write beatmaps to .osu format."""

    async def write(
        self,
        audio_analysis: AudioAnalysis,
        hit_objects: List[HitObject],
        difficulty: str,
    ) -> str:
        """Write .osu file from analysis and hit objects.
        
        Args:
            audio_analysis: Audio analysis results
            hit_objects: Generated hit objects
            difficulty: Difficulty level
            
        Returns:
            Path to generated .osu file
        """
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

        # Generate filename
        filename = f"BeatForge_{difficulty}.osu"
        filepath = os.path.join(settings.OUTPUT_DIR, filename)

        logger.info(f"Writing .osu file: {filepath}")

        # Build .osu file content
        content = self._build_osu_content(
            audio_analysis=audio_analysis,
            hit_objects=hit_objects,
            difficulty=difficulty,
        )

        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Wrote {len(hit_objects)} hit objects to {filepath}")
        return filepath

    def _build_osu_content(
        self,
        audio_analysis: AudioAnalysis,
        hit_objects: List[HitObject],
        difficulty: str,
    ) -> str:
        """Build complete .osu file content."""
        lines = []

        # Version
        lines.append("osu file format v14")
        lines.append("")

        # General section
        lines.append("[General]")
        lines.append("AudioFilename: audio.mp3")
        lines.append("AudioLeadIn: 0")
        lines.append("PreviewTime: -1")
        lines.append("Countdown: 0")
        lines.append("SampleSet: Soft")
        lines.append("StackLeniency: 0.7")
        lines.append("Mode: 0")
        lines.append("LetterboxInBreaks: 0")
        lines.append("WidescreenStoryboard: 0")
        lines.append("")

        # Editor section (optional, can be empty)
        lines.append("[Editor]")
        lines.append("DistanceSpacing: 1.0")
        lines.append("BeatDivisor: 4")
        lines.append("GridSize: 4")
        lines.append("")

        # Metadata section
        lines.append("[Metadata]")
        lines.append("Title: Auto-generated Track")
        lines.append("TitleUnicode: Auto-generated Track")
        lines.append("Artist: Unknown")
        lines.append("ArtistUnicode: Unknown")
        lines.append("Creator: BeatForge")
        lines.append("Version: " + difficulty)
        lines.append("Source: ")
        lines.append("Tags: beatforge auto-generated")
        lines.append("BeatmapID: 0")
        lines.append("BeatmapSetID: -1")
        lines.append("")

        # Difficulty section
        diff_settings = self._get_difficulty_settings(difficulty)
        lines.append("[Difficulty]")
        lines.append(f"HPDrainRate: {diff_settings['hp']}")
        lines.append(f"CircleSize: {diff_settings['cs']}")
        lines.append(f"OverallDifficulty: {diff_settings['od']}")
        lines.append(f"ApproachRate: {diff_settings['ar']}")
        lines.append(f"SliderMultiplier: {diff_settings['slider_mult']}")
        lines.append(f"SliderTickRate: {diff_settings['slider_tick']}")
        lines.append("")

        # Events section
        lines.append("[Events]")
        lines.append("0,0,\"background.jpg\",0,0")
        lines.append("")

        # TimingPoints section
        lines.append("[TimingPoints]")
        beat_duration = 60000 / audio_analysis.bpm  # Convert BPM to milliseconds per beat
        lines.append(f"0,{beat_duration},4,1,0,100,1,0")
        lines.append("")

        # HitObjects section
        lines.append("[HitObjects]")
        for obj in hit_objects:
            lines.append(self._format_hit_object(obj))
        lines.append("")

        return "\n".join(lines)

    def _get_difficulty_settings(self, difficulty: str) -> Dict:
        """Get difficulty settings."""
        settings_map = {
            "Easy": {
                "hp": 4.0,
                "cs": 4.0,
                "od": 4.0,
                "ar": 4.0,
                "slider_mult": 1.4,
                "slider_tick": 1.0,
            },
            "Normal": {
                "hp": 5.0,
                "cs": 4.0,
                "od": 5.0,
                "ar": 5.0,
                "slider_mult": 1.6,
                "slider_tick": 1.0,
            },
            "Hard": {
                "hp": 6.0,
                "cs": 3.8,
                "od": 6.0,
                "ar": 6.5,
                "slider_mult": 1.8,
                "slider_tick": 1.0,
            },
            "Insane": {
                "hp": 7.0,
                "cs": 3.5,
                "od": 8.0,
                "ar": 8.0,
                "slider_mult": 2.0,
                "slider_tick": 1.0,
            },
            "Expert+": {
                "hp": 8.0,
                "cs": 3.0,
                "od": 9.0,
                "ar": 9.5,
                "slider_mult": 2.0,
                "slider_tick": 1.0,
            },
        }
        return settings_map.get(difficulty, settings_map["Normal"])

    def _format_hit_object(self, obj: HitObject) -> str:
        """Format hit object for .osu file."""
        # Format: x,y,time,type,hitSound[,objectParams][,hitSample]
        
        if obj.object_type == ObjectType.CIRCLE:
            # Circle: x,y,time,type,hitSound,hitSample
            return f"{int(obj.x)},{int(obj.y)},{int(obj.time)},1,{obj.hit_sound},0:0:0:0:"
        
        elif obj.object_type == ObjectType.SLIDER:
            # Slider: x,y,time,type,hitSound,curveType|points,slides,length[,edgeSounds][,edgeSets][,hitSample]
            return f"{int(obj.x)},{int(obj.y)},{int(obj.time)},2,{obj.hit_sound},{obj.slider_path},1,{int(obj.slider_duration)},0:0:0:0:"
        
        elif obj.object_type == ObjectType.SPINNER:
            # Spinner: x,y,time,type,hitSound,endTime,hitSample
            return f"{int(obj.x)},{int(obj.y)},{int(obj.time)},8,{obj.hit_sound},{int(obj.time + 1000)},0:0:0:0:"
        
        return f"{int(obj.x)},{int(obj.y)},{int(obj.time)},1,{obj.hit_sound},0:0:0:0:"
