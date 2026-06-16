"""Beat detection module."""

import logging

import librosa
import numpy as np

logger = logging.getLogger(__name__)


class BeatDetector:
    """Detects beat positions given BPM."""

    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """Initialize beat detector.

        Args:
            sr: Sample rate
            hop_length: Hop length for analysis
        """
        self.sr = sr
        self.hop_length = hop_length

    def detect(self, y: np.ndarray, sr: int = None, bpm: float = None) -> np.ndarray:
        """Detect beat positions.

        Args:
            y: Audio time series
            sr: Sample rate
            bpm: Target BPM (optional)

        Returns:
            Array of beat times in seconds
        """
        if sr is None:
            sr = self.sr

        # Use librosa's beat tracking
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # Convert beat frames to time
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)

        return beat_times
