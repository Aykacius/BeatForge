"""Musical feature detection for intelligent mapping."""

import librosa
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from loguru import logger

from app.config import settings


@dataclass
class MusicalFeature:
    """Represents a detected musical feature."""
    time: float
    duration: float
    confidence: float
    feature_type: str  # kick, snare, vocal, bass, melodic, cymbal
    velocity: float  # Loudness/intensity


class KickDetector:
    """Detect kick drum patterns."""

    def detect(self, y: np.ndarray, sr: int) -> List[MusicalFeature]:
        """Detect kick drum hits.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            List of detected kicks
        """
        # Use onset detection with low-frequency emphasis
        # Kick drums are typically in 20-150 Hz range
        
        # Extract low-frequency content
        D = librosa.stft(y)
        S = np.abs(D)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=len(D))
        
        # Isolate low frequencies
        low_freq_mask = frequencies < 150
        S_low = S[low_freq_mask, :]
        
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(S=S_low, sr=sr)
        
        # Detect peaks
        peaks = librosa.util.peak_pick(
            onset_env,
            pre_max=3,
            post_max=3,
            pre_avg=3,
            post_avg=3,
            delta=0.3,
            wait=10,
        )
        
        times = librosa.frames_to_time(peaks, sr=sr)
        
        # Extract velocity from onset strength
        features = []
        for t, peak_idx in zip(times, peaks):
            velocity = float(onset_env[peak_idx] / np.max(onset_env))
            features.append(MusicalFeature(
                time=float(t),
                duration=0.05,
                confidence=min(1.0, velocity * 1.5),
                feature_type="kick",
                velocity=velocity,
            ))
        
        return features


class SnareDetector:
    """Detect snare drum and hi-hat patterns."""

    def detect(self, y: np.ndarray, sr: int) -> List[MusicalFeature]:
        """Detect snare hits.
        
        Snares are typically 1-4 kHz with sharp attacks.
        """
        # Mid-frequency content (snare range)
        D = librosa.stft(y)
        S = np.abs(D)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=len(D))
        
        # Isolate mid frequencies (snare range)
        mid_freq_mask = (frequencies > 1000) & (frequencies < 5000)
        S_mid = S[mid_freq_mask, :]
        
        # Compute onset strength with high-pass emphasis
        onset_env = librosa.onset.onset_strength(S=S_mid, sr=sr)
        
        # Detect peaks with stricter threshold
        peaks = librosa.util.peak_pick(
            onset_env,
            pre_max=2,
            post_max=2,
            pre_avg=3,
            post_avg=3,
            delta=0.4,
            wait=8,
        )
        
        times = librosa.frames_to_time(peaks, sr=sr)
        
        features = []
        for t, peak_idx in zip(times, peaks):
            velocity = float(onset_env[peak_idx] / np.max(onset_env))
            features.append(MusicalFeature(
                time=float(t),
                duration=0.03,
                confidence=min(1.0, velocity * 1.2),
                feature_type="snare",
                velocity=velocity,
            ))
        
        return features


class VocalPeakDetector:
    """Detect vocal peaks and melodic lines."""

    def detect(self, y: np.ndarray, sr: int) -> List[MusicalFeature]:
        """Detect vocal peaks.
        
        Vocals are typically 100-4000 Hz with sustained energy.
        """
        # Extract vocal range frequencies
        D = librosa.stft(y)
        S = np.abs(D)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=len(D))
        
        vocal_mask = (frequencies > 80) & (frequencies < 4000)
        S_vocal = S[vocal_mask, :]
        
        # Compute energy envelope (not just onsets)
        energy = librosa.feature.rms(y=y)[0]
        
        # Find peaks in energy
        threshold = np.mean(energy) + np.std(energy)
        peaks = librosa.util.peak_pick(
            energy,
            pre_max=5,
            post_max=5,
            pre_avg=10,
            post_avg=10,
            delta=0.1,
            wait=15,
        )
        
        times = librosa.frames_to_time(peaks, sr=sr)
        
        features = []
        for t, peak_idx in zip(times, peaks):
            velocity = float(energy[peak_idx] / np.max(energy))
            features.append(MusicalFeature(
                time=float(t),
                duration=0.2,  # Vocals sustain longer
                confidence=min(1.0, velocity * 0.8),
                feature_type="vocal",
                velocity=velocity,
            ))
        
        return features


class BassLineDetector:
    """Detect bass line patterns."""

    def detect(self, y: np.ndarray, sr: int) -> List[MusicalFeature]:
        """Detect bass line notes.
        
        Bass is typically 20-200 Hz with melodic content.
        """
        # Extract bass frequencies
        D = librosa.stft(y)
        S = np.abs(D)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=len(D))
        
        bass_mask = frequencies < 200
        S_bass = S[bass_mask, :]
        
        # Track bass notes using chroma
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_bass = chroma[:, :S_bass.shape[1]]  # Align with STFT
        
        # Find note onsets
        onset_env = librosa.onset.onset_strength(S=S_bass, sr=sr)
        peaks = librosa.util.peak_pick(
            onset_env,
            pre_max=4,
            post_max=4,
            pre_avg=3,
            post_avg=3,
            delta=0.2,
            wait=12,
        )
        
        times = librosa.frames_to_time(peaks, sr=sr)
        
        features = []
        for t, peak_idx in zip(times, peaks):
            velocity = float(onset_env[peak_idx] / np.max(onset_env))
            features.append(MusicalFeature(
                time=float(t),
                duration=0.15,
                confidence=min(1.0, velocity),
                feature_type="bass",
                velocity=velocity,
            ))
        
        return features


class CymbalDetector:
    """Detect cymbals and hi-hats."""

    def detect(self, y: np.ndarray, sr: int) -> List[MusicalFeature]:
        """Detect cymbal hits.
        
        Cymbals are high-frequency (4000+ Hz) with quick decay.
        """
        D = librosa.stft(y)
        S = np.abs(D)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=len(D))
        
        # High-frequency content
        cymbal_mask = frequencies > 4000
        S_cymbal = S[cymbal_mask, :]
        
        onset_env = librosa.onset.onset_strength(S=S_cymbal, sr=sr)
        
        peaks = librosa.util.peak_pick(
            onset_env,
            pre_max=2,
            post_max=2,
            pre_avg=3,
            post_avg=3,
            delta=0.35,
            wait=6,
        )
        
        times = librosa.frames_to_time(peaks, sr=sr)
        
        features = []
        for t, peak_idx in zip(times, peaks):
            velocity = float(onset_env[peak_idx] / np.max(onset_env))
            features.append(MusicalFeature(
                time=float(t),
                duration=0.02,
                confidence=min(1.0, velocity * 0.9),
                feature_type="cymbal",
                velocity=velocity,
            ))
        
        return features


class MusicalFeatureExtractor:
    """Main orchestrator for musical feature extraction."""

    def __init__(self):
        """Initialize detectors."""
        self.kick_detector = KickDetector()
        self.snare_detector = SnareDetector()
        self.vocal_detector = VocalPeakDetector()
        self.bass_detector = BassLineDetector()
        self.cymbal_detector = CymbalDetector()

    async def extract(self, y: np.ndarray, sr: int) -> Dict[str, List[MusicalFeature]]:
        """Extract all musical features.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary of detected features by type
        """
        logger.info("Extracting musical features...")
        
        features = {
            "kicks": self.kick_detector.detect(y, sr),
            "snares": self.snare_detector.detect(y, sr),
            "vocals": self.vocal_detector.detect(y, sr),
            "bass": self.bass_detector.detect(y, sr),
            "cymbals": self.cymbal_detector.detect(y, sr),
        }
        
        logger.info(f"  Kicks: {len(features['kicks'])}")
        logger.info(f"  Snares: {len(features['snares'])}")
        logger.info(f"  Vocals: {len(features['vocals'])}")
        logger.info(f"  Bass: {len(features['bass'])}")
        logger.info(f"  Cymbals: {len(features['cymbals'])}")
        
        return features
