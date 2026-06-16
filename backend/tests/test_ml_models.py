"""Integration tests for ML models."""

import pytest
import numpy as np
from app.ml.enhanced_inference import (
    EnhancedInferenceEngine,
    PatternPredictorModel,
    StarRatingModel,
    StyleClassifierModel,
)
from app.ml.preprocessing import AudioFeatureExtractor, MusicalFeatureExtractor


@pytest.fixture
async def inference_engine():
    """Create inference engine."""
    return EnhancedInferenceEngine()


@pytest.fixture
def sample_audio_features():
    """Sample audio features."""
    return {
        "bpm": 140,
        "beat_times": np.linspace(0, 180, 200),
        "onset_times": np.linspace(0, 180, 400),
        "energy": np.random.rand(400),
        "spectral_features": {
            "centroid": 3000,
            "rolloff": 8000,
            "mean_energy": -20,
            "max_energy": 0,
        },
        "sections": [
            {"label": "intro", "start": 0, "end": 30, "duration": 30},
            {"label": "verse", "start": 30, "end": 90, "duration": 60},
            {"label": "drop", "start": 90, "end": 150, "duration": 60},
            {"label": "outro", "start": 150, "end": 180, "duration": 30},
        ],
        "duration": 180,
    }


@pytest.fixture
def sample_musical_features():
    """Sample musical features."""
    class MockFeature:
        def __init__(self, time, velocity, duration=0.1):
            self.time = time
            self.velocity = velocity
            self.duration = duration
    
    return {
        "kicks": [MockFeature(t, 0.8) for t in [0, 1.5, 3, 4.5]],
        "snares": [MockFeature(t, 0.7) for t in [0.75, 2.25, 3.75]],
        "vocals": [MockFeature(t, 0.6, 0.5) for t in [45, 75, 120]],
        "bass": [MockFeature(t, 0.5) for t in np.linspace(0, 180, 50)],
        "cymbals": [MockFeature(t, 0.4) for t in [0, 30, 60, 90, 120, 150]],
    }


@pytest.mark.asyncio
async def test_pattern_prediction(sample_audio_features, sample_musical_features):
    """Test pattern prediction model."""
    model = PatternPredictorModel()
    
    context = {"section": "drop", "energy": 0.85, "difficulty_level": 0.7}
    pattern, confidence, probs = await model.predict(
        sample_audio_features, sample_musical_features, context
    )
    
    assert isinstance(pattern, str)
    assert pattern in model.patterns
    assert 0 <= confidence <= 1
    assert len(probs) == len(model.patterns)
    assert np.isclose(sum(probs.values()), 1.0)


@pytest.mark.asyncio
async def test_star_rating_prediction():
    """Test star rating prediction model."""
    model = StarRatingModel()
    
    beatmap_features = {
        "avg_spacing": 120,
        "max_spacing": 250,
        "min_spacing": 60,
        "object_density": 0.6,
        "circle_density": 0.3,
        "slider_density": 0.2,
        "stream_density": 0.1,
        "stream_length": 8,
        "jump_count": 5,
    }
    
    sr, confidence = await model.predict(beatmap_features)
    
    assert 2.0 <= sr <= 9.0
    assert 0 <= confidence <= 1


@pytest.mark.asyncio
async def test_style_classification(sample_audio_features):
    """Test style classifier model."""
    model = StyleClassifierModel()
    
    hit_objects = [
        {"x": 256, "y": 192, "time": 0, "type": "circle"},
        {"x": 300, "y": 150, "time": 100, "type": "circle"},
        {"x": 200, "y": 250, "time": 200, "type": "circle"},
        {"x": 350, "y": 200, "time": 300, "type": "circle"},
    ]
    
    style, confidence, probs = await model.predict(hit_objects)
    
    assert isinstance(style, str)
    assert style in model.styles
    assert 0 <= confidence <= 1
    assert len(probs) == len(model.styles)


@pytest.mark.asyncio
async def test_inference_engine(sample_audio_features, sample_musical_features):
    """Test complete inference engine."""
    engine = EnhancedInferenceEngine()
    
    context = {"section": "drop", "energy": 0.8}
    pattern, confidence = await engine.predict_next_pattern(
        sample_audio_features, sample_musical_features, context
    )
    
    assert isinstance(pattern, str)
    assert 0 <= confidence <= 1


def test_feature_extraction(sample_audio_features):
    """Test feature extraction."""
    features = AudioFeatureExtractor.extract_for_pattern_prediction(sample_audio_features)
    
    assert features.shape == (100,)
    assert np.all(np.isfinite(features))


def test_star_rating_features():
    """Test star rating feature extraction."""
    beatmap_features = {
        "avg_spacing": 100,
        "max_spacing": 200,
        "object_density": 0.5,
    }
    
    features = AudioFeatureExtractor.extract_for_star_rating(beatmap_features)
    
    assert features.shape == (50,)
    assert np.all(np.isfinite(features))
