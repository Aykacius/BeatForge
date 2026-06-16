"""Energy extraction module."""

import logging

import librosa
import numpy as np

logger = logging.getLogger(__name__)


class EnergyDetector:
    """Extracts RMS energy and energy curves."""

    def __init__(self, sr: int = 22050, hop_length: int = 512, n_fft: int = 2048):
        """Initialize energy detector.

        Args:
            sr: Sample rate
            hop_length: Hop length
            n_fft: FFT window size
        """
        self.sr = sr
        self.hop_length = hop_length
        self.n_fft = n_fft

    def extract(self, S: np.ndarray = None, y: np.ndarray = None, sr: int = None) -> np.ndarray:
        """Extract energy from audio or spectrogram.

        Args:
            S: Spectrogram (optional, use if available)
            y: Audio time series (optional)
            sr: Sample rate

        Returns:
            Energy curve as normalized array
        """
        if sr is None:
            sr = self.sr

        if S is not None:
            # Compute energy from spectrogram
            energy = np.sqrt(np.sum(S ** 2, axis=0))
        elif y is not None:
            # Compute RMS energy
            energy = librosa.feature.rms(
                y=y, frame_length=self.n_fft, hop_length=self.hop_length
            )[0]
        else:
            raise ValueError("Either S or y must be provided")

        # Normalize
        energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-8)

        return energy
