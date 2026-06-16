"""OSZ package creation and handling."""

import logging
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


class OSZPackager:
    """Creates .osz (zip archive) packages containing beatmap and audio."""

    def package(
        self,
        osu_file_path: str,
        audio_file_path: str,
        output_path: str,
        beatmap_name: str = "Beatmap",
    ) -> str:
        """Create .osz package.

        Args:
            osu_file_path: Path to .osu file
            audio_file_path: Path to audio file
            output_path: Output .osz file path
            beatmap_name: Name for beatmap in archive

        Returns:
            Path to created .osz file
        """
        logger.info(f"Creating OSZ package: {output_path}")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as osz:
            # Add .osu file
            arcname_osu = f"{beatmap_name}.osu"
            osz.write(osu_file_path, arcname=arcname_osu)
            logger.info(f"Added {arcname_osu} to package")

            # Add audio file
            arcname_audio = f"audio.mp3"
            osz.write(audio_file_path, arcname=arcname_audio)
            logger.info(f"Added audio file to package")

        logger.info(f"OSZ package created: {output_path}")
        return output_path
