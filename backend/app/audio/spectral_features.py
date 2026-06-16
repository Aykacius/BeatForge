"""Spectral feature extraction module."""

import logging

import librosa
import numpy as np

logger = logging.getLogger(__name__)


class SpectralFeatures:
    """Extracts spectral features from audio."""

    def __init__(self, sr: int = 22050, hop_length: int = 512, n_fft: int = 2048):
        """Initialize spectral features extractor.

        Args:
            sr: Sample rate
            hop_length: Hop length
            n_fft: FFT window size
        """
        self.sr = sr
        self.hop_length = hop_length
        self.n_fft = n_fft

    def extract(self, y: np.ndarray, S: np.ndarray = None, sr: int = None) -> dict:
        """Extract multiple spectral features.

        Args:
            y: Audio time series
            S: Spectrogram (optional)
            sr: Sample rate

        Returns:
            Dictionary with spectral features
        """
        if sr is None:
            sr = self.sr

        if S is None:
            S = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))

        features = {}

        # Spectral centroid
        spec_cent = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
        features["spectral_centroid"] = {
            "mean": float(np.mean(spec_cent)),
            "std": float(np.std(spec_cent)),
            "values": spec_cent.tolist(),
        }

        # Spectral rolloff
        spec_roll = librosa.feature.spectral_rolloff(S=S, sr=sr)[0]
        features["spectral_rolloff"] = {
            "mean": float(np.mean(spec_roll)),
            "std": float(np.std(spec_roll)),
        }

        # MFCC (Mel-Frequency Cepstral Coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features["mfcc"] = {
            "mean": np.mean(mfcc, axis=1).tolist(),
            "std": np.std(mfcc, axis=1).tolist(),
        }

        # Chroma features
        chroma = librosa.feature.chroma_stft(S=S, sr=sr)
        features["chroma"] = {
            "mean": np.mean(chroma, axis=1).tolist(),
            "std": np.std(chroma, axis=1).tolist(),
        }

        return features
