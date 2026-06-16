"""Unit tests for audio analyzer."""

import pytest
import numpy as np
from app.audio.analyzer import AudioAnalyzer
from app.audio.processors import BPMDetector, BeatDetector, OnsetDetector


@pytest.fixture
def sample_audio():
    """Generate sample audio for testing."""
    sr = 44100
    duration = 3
    t = np.linspace(0, duration, sr * duration)
    # Generate a simple sine wave at 440 Hz
    y = np.sin(2 * np.pi * 440 * t)
    return y, sr


def test_bpm_detector(sample_audio):
    """Test BPM detection."""
    y, sr = sample_audio
    detector = BPMDetector()
    bpm = detector.detect(y, sr)
    
    assert isinstance(bpm, float)
    assert 0 < bpm < 300  # Reasonable BPM range


def test_beat_detector(sample_audio):
    """Test beat detection."""
    y, sr = sample_audio
    detector = BeatDetector()
    beat_frames, beat_times = detector.detect(y, sr)
    
    assert len(beat_frames) > 0
    assert len(beat_times) == len(beat_frames)
    assert np.all(beat_times >= 0)
    assert np.all(np.diff(beat_times) > 0)  # Times should be increasing


def test_onset_detector(sample_audio):
    """Test onset detection."""
    y, sr = sample_audio
    detector = OnsetDetector()
    onset_frames, onset_times = detector.detect(y, sr)
    
    assert len(onset_frames) >= 0
    assert len(onset_times) == len(onset_frames)
