"""Silence detection module."""

import logging

import librosa
import numpy as np

logger = logging.getLogger(__name__)


class SilenceDetector:
    """Detects silent portions of audio."""

    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """Initialize silence detector.

        Args:
            sr: Sample rate
            hop_length: Hop length
        """
        self.sr = sr
        self.hop_length = hop_length

    def detect(self, S: np.ndarray, sr: int = None, threshold_db: float = -60) -> list[dict]:
        """Detect silence in audio.

        Args:
            S: Spectrogram
            sr: Sample rate
            threshold_db: Threshold in dB below which to consider silence

        Returns:
            List of silence segments with start/end times
        """
        if sr is None:
            sr = self.sr

        # Convert to dB
        S_db = librosa.power_to_db(S, ref=np.max(S))

        # Find silent frames
        is_silent = np.mean(S_db, axis=0) < threshold_db

        # Find transitions
        transitions = np.diff(is_silent.astype(int))
        starts = np.where(transitions == 1)[0]
        ends = np.where(transitions == -1)[0]

        # Handle edge cases
        if is_silent[0]:
            starts = np.concatenate([[0], starts])
        if is_silent[-1]:
            ends = np.concatenate([ends, [len(is_silent)]])

        # Convert frames to time
        segments = []
        for start, end in zip(starts, ends):
            segment = {
                "start_time": float(librosa.frames_to_time(start, sr=sr, hop_length=self.hop_length)),
                "end_time": float(librosa.frames_to_time(end, sr=sr, hop_length=self.hop_length)),
                "duration": float(
                    librosa.frames_to_time(
                        end - start, sr=sr, hop_length=self.hop_length
                    )
                ),
            }
            segments.append(segment)

        return segments
