"""Musical section detection module."""

import logging

import librosa
import numpy as np
from scipy import signal as scipy_signal

logger = logging.getLogger(__name__)


class SectionDetector:
    """Detects musical sections (intro, verse, drop, etc.)."""

    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """Initialize section detector.

        Args:
            sr: Sample rate
            hop_length: Hop length
        """
        self.sr = sr
        self.hop_length = hop_length

    def detect(self, y: np.ndarray, S: np.ndarray = None, sr: int = None) -> list[dict]:
        """Detect musical sections.

        Args:
            y: Audio time series
            S: Spectrogram (optional)
            sr: Sample rate

        Returns:
            List of section dictionaries with start_time, end_time, type
        """
        if sr is None:
            sr = self.sr

        if S is None:
            S = np.abs(librosa.stft(y))

        # Compute MFCCs for section detection
        mfcc = librosa.feature.mfcc(S=librosa.power_to_db(S), n_mfcc=13)

        # Compute recurrence matrix
        rec = librosa.sequence.transition_loop_or_jump(mfcc.shape[1], fmin=2, fmax=10)
        rec = np.dot(mfcc.T, mfcc)

        # Find novelty peaks (section boundaries)
        novelty = np.sqrt(np.sum(np.diff(rec) ** 2, axis=0))
        peaks, _ = scipy_signal.find_peaks(
            novelty, distance=sr // self.hop_length, prominence=np.std(novelty)
        )

        # Convert frame indices to time
        boundaries = librosa.frames_to_time(np.concatenate([[0], peaks, [len(mfcc[0])]]), sr=sr)

        sections = []
        section_types = ["intro", "verse", "build", "drop", "break", "outro"]

        for i in range(len(boundaries) - 1):
            section = {
                "start_time": float(boundaries[i]),
                "end_time": float(boundaries[i + 1]),
                "duration": float(boundaries[i + 1] - boundaries[i]),
                "type": section_types[i % len(section_types)],
                "index": i,
            }
            sections.append(section)

        return sections
