"""BPM detection module."""

import logging

import librosa
import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)


class BPMDetector:
    """Detects BPM using onset-based autocorrelation."""

    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """Initialize BPM detector.

        Args:
            sr: Sample rate
            hop_length: Hop length for analysis
        """
        self.sr = sr
        self.hop_length = hop_length

    def detect(self, y: np.ndarray, sr: int = None) -> float:
        """Detect BPM from audio.

        Args:
            y: Audio time series
            sr: Sample rate (uses self.sr if not provided)

        Returns:
            Estimated BPM as float
        """
        if sr is None:
            sr = self.sr

        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        # Auto-correlate to find periodicity
        # Assume BPM is between 60-200
        min_bpm = 60
        max_bpm = 200

        # Convert BPM range to frame range
        min_period = int(np.round(sr * 60 / (max_bpm * self.hop_length)))
        max_period = int(np.round(sr * 60 / (min_bpm * self.hop_length)))

        # Compute autocorrelation
        autocorr = np.correlate(onset_env, onset_env, mode="full")
        autocorr = autocorr[len(autocorr) // 2 :]

        # Find peaks in valid BPM range
        peaks, _ = signal.find_peaks(
            autocorr[min_period:max_period],
            distance=min_period // 4,
            prominence=np.max(autocorr[min_period:max_period]) * 0.1,
        )

        if len(peaks) == 0:
            # Fallback: use maximum in range
            peak_idx = np.argmax(autocorr[min_period:max_period]) + min_period
        else:
            # Use highest peak
            peak_idx = peaks[np.argmax(autocorr[min_period:max_period][peaks])] + min_period

        # Convert frame lag to BPM
        bpm = 60.0 * sr / (self.hop_length * peak_idx)
        bpm = np.clip(bpm, min_bpm, max_bpm)

        return float(bpm)
