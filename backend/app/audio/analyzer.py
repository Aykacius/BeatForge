"""Core audio analysis engine."""

import librosa
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from loguru import logger

from app.config import settings
from app.audio.processors import (
    BPMDetector,
    BeatDetector,
    OnsetDetector,
    EnergyAnalyzer,
    SectionDetector,
    TempoAnalyzer,
    SilenceDetector,
    SpectralAnalyzer,
)


@dataclass
class AudioAnalysis:
    """Complete audio analysis results."""
    bpm: float
    beat_times: np.ndarray
    beat_frames: np.ndarray
    onset_times: np.ndarray
    onset_frames: np.ndarray
    energy: np.ndarray
    energy_times: np.ndarray
    sections: List[Dict]
    tempo_changes: List[Dict]
    silence_intervals: List[Tuple[float, float]]
    duration: float
    sample_rate: int
    spectral_features: Dict


class AudioAnalyzer:
    """Comprehensive audio analysis for beatmap generation."""

    def __init__(self, sample_rate: int = settings.SAMPLE_RATE):
        """Initialize audio analyzer.
        
        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.hop_length = settings.HOP_LENGTH
        self.n_fft = settings.N_FFT

        # Initialize sub-analyzers
        self.bpm_detector = BPMDetector()
        self.beat_detector = BeatDetector()
        self.onset_detector = OnsetDetector()
        self.energy_analyzer = EnergyAnalyzer()
        self.section_detector = SectionDetector()
        self.tempo_analyzer = TempoAnalyzer()
        self.silence_detector = SilenceDetector()
        self.spectral_analyzer = SpectralAnalyzer()

    async def analyze(self, file_path: str) -> AudioAnalysis:
        """Perform comprehensive audio analysis.
        
        Args:
            file_path: Path to MP3 or audio file
            
        Returns:
            AudioAnalysis object with all features
        """
        logger.info(f"Loading audio from {file_path}")
        
        # Load audio
        y, sr = librosa.load(file_path, sr=self.sample_rate)
        duration = librosa.get_duration(y=y, sr=sr)
        
        logger.info(f"  Loaded {duration:.2f}s of audio at {sr}Hz")

        # Compute spectrogram and other features
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
        S_db = librosa.power_to_db(S, ref=np.max)

        logger.info("Detecting BPM...")
        bpm = self.bpm_detector.detect(y, sr)
        
        logger.info("Detecting beats...")
        beat_frames, beat_times = self.beat_detector.detect(y, sr)
        
        logger.info("Detecting onsets...")
        onset_frames, onset_times = self.onset_detector.detect(y, sr)
        
        logger.info("Analyzing energy...")
        energy, energy_times = self.energy_analyzer.analyze(y, sr)
        
        logger.info("Detecting sections...")
        sections = self.section_detector.detect(y, sr)
        
        logger.info("Detecting tempo changes...")
        tempo_changes = self.tempo_analyzer.analyze(y, sr)
        
        logger.info("Detecting silence...")
        silence_intervals = self.silence_detector.detect(y, sr)
        
        logger.info("Analyzing spectral features...")
        spectral_features = self.spectral_analyzer.analyze(S_db, sr)

        analysis = AudioAnalysis(
            bpm=bpm,
            beat_times=beat_times,
            beat_frames=beat_frames,
            onset_times=onset_times,
            onset_frames=onset_frames,
            energy=energy,
            energy_times=energy_times,
            sections=sections,
            tempo_changes=tempo_changes,
            silence_intervals=silence_intervals,
            duration=duration,
            sample_rate=sr,
            spectral_features=spectral_features,
        )

        logger.info(f"Analysis complete: BPM={bpm}, Duration={duration:.2f}s")
        logger.info(f"  Beats: {len(beat_times)}")
        logger.info(f"  Onsets: {len(onset_times)}")
        logger.info(f"  Sections: {len(sections)}")

        return analysis
