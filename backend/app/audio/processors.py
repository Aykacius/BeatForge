"""Audio processing and feature extraction components."""

import librosa
import numpy as np
from typing import Dict, List, Tuple
from loguru import logger

from app.config import settings


class BPMDetector:
    """Detect BPM from audio signal."""

    def detect(self, y: np.ndarray, sr: int) -> float:
        """Detect BPM using onset strength and autocorrelation.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Estimated BPM
        """
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Estimate BPM using autocorrelation
        bpm = librosa.feature.tempogram_ratio(onset_env=onset_env, sr=sr)
        
        # Alternative: use the simpler but effective method
        bpm = librosa.beat.tempo(y=y, sr=sr)[0]
        
        return float(bpm)


class BeatDetector:
    """Detect beat frames and times from audio."""

    def detect(self, y: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """Detect beats using onset strength and dynamic programming.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Tuple of (beat_frames, beat_times)
        """
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Estimate BPM
        bpm = librosa.beat.tempo(y=y, sr=sr)[0]
        
        # Track beats
        beat_frames = librosa.beat.beat_track(onset_env=onset_env, sr=sr, bpm=bpm)[1]
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        return beat_frames, beat_times


class OnsetDetector:
    """Detect onset times (note attacks)."""

    def detect(self, y: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """Detect onsets using spectral flux.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Tuple of (onset_frames, onset_times)
        """
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Pick peaks in onset strength
        onset_frames = librosa.util.peak_pick(
            onset_env,
            pre_max=3,
            post_max=3,
            pre_avg=3,
            post_avg=3,
            delta=0.1,
            wait=10,
        )
        
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        return onset_frames, onset_times


class EnergyAnalyzer:
    """Analyze energy envelope of audio."""

    def analyze(self, y: np.ndarray, sr: int, hop_length: int = settings.HOP_LENGTH) -> Tuple[np.ndarray, np.ndarray]:
        """Extract RMS energy over time.
        
        Args:
            y: Audio time series
            sr: Sample rate
            hop_length: Hop length for STFT
            
        Returns:
            Tuple of (energy, time_frames)
        """
        energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)
        
        return energy, times


class SectionDetector:
    """Detect song sections (intro, verse, drop, etc)."""

    def detect(self, y: np.ndarray, sr: int, n_segments: int = 6) -> List[Dict]:
        """Detect structural sections using chroma and self-similarity.
        
        Args:
            y: Audio time series
            sr: Sample rate
            n_segments: Number of segments to identify
            
        Returns:
            List of section dictionaries with start/end times and labels
        """
        # Compute chroma features
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # Compute self-similarity matrix
        R = librosa.sequence.transition_loop(n_segments, [0.5, 0.5])
        P, state = librosa.sequence.viterbi_discriminative(
            chroma, R, np.ones((n_segments, chroma.shape[1]))
        )
        
        # Get segment boundaries
        boundaries = librosa.segment.agglomerative(chroma, n_segments)
        segment_times = librosa.frames_to_time(boundaries, sr=sr)
        
        # Label sections
        section_labels = ["intro", "verse", "build", "drop", "break", "outro"]
        sections = []
        
        for i in range(len(segment_times) - 1):
            sections.append({
                "label": section_labels[i % len(section_labels)],
                "start": float(segment_times[i]),
                "end": float(segment_times[i + 1]),
                "duration": float(segment_times[i + 1] - segment_times[i]),
            })
        
        return sections


class TempoAnalyzer:
    """Analyze tempo variations throughout the song."""

    def analyze(self, y: np.ndarray, sr: int, window_size: int = 10000) -> List[Dict]:
        """Detect tempo changes over time.
        
        Args:
            y: Audio time series
            sr: Sample rate
            window_size: Window size for tempo analysis
            
        Returns:
            List of tempo change events
        """
        # Compute tempogram
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempogram = librosa.feature.tempogram(onset_env=onset_env, sr=sr)
        
        # Analyze tempo stability
        tempo_changes = []
        # TODO: Implement tempo change detection
        
        return tempo_changes


class SilenceDetector:
    """Detect silence intervals in the audio."""

    def detect(self, y: np.ndarray, sr: int, threshold_db: float = -40) -> List[Tuple[float, float]]:
        """Find silent intervals.
        
        Args:
            y: Audio time series
            sr: Sample rate
            threshold_db: Silence threshold in dB
            
        Returns:
            List of (start_time, end_time) tuples for silent intervals
        """
        # Compute RMS energy
        energy = librosa.feature.rms(y=y)[0]
        energy_db = librosa.power_to_db(energy, ref=np.max)
        
        # Find frames below threshold
        silent_frames = energy_db < threshold_db
        
        # Convert frames to times
        times = librosa.frames_to_time(np.arange(len(energy)), sr=sr)
        
        silence_intervals = []
        in_silence = False
        start = 0
        
        for i, is_silent in enumerate(silent_frames):
            if is_silent and not in_silence:
                start = times[i]
                in_silence = True
            elif not is_silent and in_silence:
                silence_intervals.append((start, times[i]))
                in_silence = False
        
        return silence_intervals


class SpectralAnalyzer:
    """Analyze spectral characteristics."""

    def analyze(self, S_db: np.ndarray, sr: int) -> Dict:
        """Extract spectral features.
        
        Args:
            S_db: Mel spectrogram in dB scale
            sr: Sample rate
            
        Returns:
            Dictionary with spectral features
        """
        # Compute spectral centroid
        spectral_centroid = np.mean(np.argmax(S_db, axis=0))
        
        # Compute spectral rolloff
        spectral_rolloff = np.mean(np.where(S_db.cumsum(axis=0) > 0.85 * S_db.sum(axis=0))[0])
        
        return {
            "centroid": float(spectral_centroid),
            "rolloff": float(spectral_rolloff),
            "mean_energy": float(np.mean(S_db)),
            "max_energy": float(np.max(S_db)),
        }
