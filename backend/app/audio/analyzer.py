"""Main audio analysis orchestrator."""

import logging
from pathlib import Path

import librosa
import numpy as np

from app.audio.bpm_detector import BPMDetector
from app.audio.beat_detector import BeatDetector
from app.audio.energy_detector import EnergyDetector
from app.audio.spectral_features import SpectralFeatures
from app.audio.section_detector import SectionDetector
from app.audio.silence_detector import SilenceDetector
from app.utils.exceptions import AudioAnalysisError

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Orchestrates complete audio analysis pipeline."""

    def __init__(self, sr: int = 22050, hop_length: int = 512, n_fft: int = 2048):
        """Initialize audio analyzer.

        Args:
            sr: Sample rate (Hz)
            hop_length: Hop length for STFT
            n_fft: FFT window size
        """
        self.sr = sr
        self.hop_length = hop_length
        self.n_fft = n_fft

        self.bpm_detector = BPMDetector(sr=sr, hop_length=hop_length)
        self.beat_detector = BeatDetector(sr=sr, hop_length=hop_length)
        self.energy_detector = EnergyDetector(sr=sr, hop_length=hop_length, n_fft=n_fft)
        self.spectral_features = SpectralFeatures(sr=sr, hop_length=hop_length, n_fft=n_fft)
        self.section_detector = SectionDetector(sr=sr, hop_length=hop_length)
        self.silence_detector = SilenceDetector(sr=sr, hop_length=hop_length)

    def analyze(self, audio_path: str) -> dict:
        """Run complete audio analysis pipeline.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with all analysis results
        """
        logger.info(f"Starting audio analysis: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr)
            duration = librosa.get_duration(y=y, sr=sr)
            logger.info(f"Audio loaded: duration={duration:.2f}s, sr={sr}Hz")

            # Compute STFT
            S = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
            logger.info(f"STFT computed: shape={S.shape}")

            # Run analysis modules
            bpm = self.bpm_detector.detect(y=y, sr=sr)
            logger.info(f"BPM detected: {bpm:.1f}")

            beats = self.beat_detector.detect(y=y, sr=sr, bpm=bpm)
            logger.info(f"Beats detected: count={len(beats)}")

            energy = self.energy_detector.extract(S=S, sr=sr)
            logger.info(f"Energy extracted: shape={energy.shape}")

            spectral = self.spectral_features.extract(y=y, S=S, sr=sr)
            logger.info(f"Spectral features extracted: {list(spectral.keys())}")

            sections = self.section_detector.detect(y=y, S=S, sr=sr)
            logger.info(f"Sections detected: count={len(sections)}")

            silence = self.silence_detector.detect(S=S, sr=sr)
            logger.info(f"Silence detected: count={len(silence)}")

            analysis_result = {
                "duration": float(duration),
                "bpm": float(bpm),
                "beats": beats.tolist() if isinstance(beats, np.ndarray) else beats,
                "energy": energy.tolist() if isinstance(energy, np.ndarray) else energy,
                "spectral_features": spectral,
                "sections": sections,
                "silence_segments": silence,
            }

            logger.info("Audio analysis completed successfully")
            return analysis_result

        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            raise AudioAnalysisError(f"Failed to analyze audio: {str(e)}")
