"""Feature engineering and preprocessing for ML models."""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import json


@dataclass
class FeatureNormalizer:
    """Normalize features for model input."""
    scaler_type: str = "standard"  # standard or minmax
    
    def __post_init__(self):
        if self.scaler_type == "standard":
            self.scaler = StandardScaler()
        elif self.scaler_type == "minmax":
            self.scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaler type: {self.scaler_type}")
    
    def fit(self, X: np.ndarray) -> None:
        """Fit scaler on training data."""
        self.scaler.fit(X)
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data."""
        return self.scaler.transform(X)
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform data."""
        return self.scaler.fit_transform(X)
    
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """Inverse transform data."""
        return self.scaler.inverse_transform(X)


class AudioFeatureExtractor:
    """Extract audio features for model input."""

    @staticmethod
    def extract_for_pattern_prediction(audio_analysis: Dict) -> np.ndarray:
        """Extract 100-dim feature vector for pattern prediction.
        
        Args:
            audio_analysis: From AudioAnalyzer
            
        Returns:
            100-dimensional feature vector
        """
        features = []
        
        # BPM features (5 dims)
        bpm = audio_analysis.get("bpm", 120)
        features.extend([
            bpm / 200,  # Normalized BPM
            (bpm % 120) / 120,  # BPM modulo
            1 if bpm > 140 else 0,  # Fast flag
            1 if bpm < 100 else 0,  # Slow flag
            1 if 100 <= bpm <= 140 else 0,  # Normal flag
        ])
        
        # Beat features (10 dims)
        beat_times = audio_analysis.get("beat_times", [])
        if len(beat_times) > 0:
            beat_intervals = np.diff(beat_times)
            features.extend([
                np.mean(beat_intervals),
                np.std(beat_intervals),
                np.min(beat_intervals),
                np.max(beat_intervals),
                len(beat_times) / audio_analysis.get("duration", 1),
                np.percentile(beat_intervals, 25),
                np.percentile(beat_intervals, 50),
                np.percentile(beat_intervals, 75),
                np.kurtosis(beat_intervals) if len(beat_intervals) > 1 else 0,
                np.skew(beat_intervals) if len(beat_intervals) > 1 else 0,
            ])
        else:
            features.extend([0] * 10)
        
        # Onset features (10 dims)
        onset_times = audio_analysis.get("onset_times", [])
        if len(onset_times) > 0:
            onset_intervals = np.diff(onset_times)
            features.extend([
                np.mean(onset_intervals),
                np.std(onset_intervals),
                np.min(onset_intervals),
                np.max(onset_intervals),
                len(onset_times) / audio_analysis.get("duration", 1),
                np.percentile(onset_intervals, 25),
                np.percentile(onset_intervals, 50),
                np.percentile(onset_intervals, 75),
                np.kurtosis(onset_intervals) if len(onset_intervals) > 1 else 0,
                np.skew(onset_intervals) if len(onset_intervals) > 1 else 0,
            ])
        else:
            features.extend([0] * 10)
        
        # Energy features (10 dims)
        energy = audio_analysis.get("energy", [])
        if len(energy) > 0:
            features.extend([
                np.mean(energy),
                np.std(energy),
                np.min(energy),
                np.max(energy),
                np.median(energy),
                np.percentile(energy, 25),
                np.percentile(energy, 75),
                np.kurtosis(energy),
                np.skew(energy),
                np.max(energy) - np.min(energy),  # Range
            ])
        else:
            features.extend([0] * 10)
        
        # Spectral features (10 dims)
        spectral = audio_analysis.get("spectral_features", {})
        features.extend([
            spectral.get("centroid", 0) / 10000,  # Normalize
            spectral.get("rolloff", 0) / 10000,
            spectral.get("mean_energy", 0),
            spectral.get("max_energy", 0),
            0, 0, 0, 0, 0, 0,  # Placeholder for future features
        ])
        
        # Section features (10 dims)
        sections = audio_analysis.get("sections", [])
        if len(sections) > 0:
            section_durations = [s.get("duration", 0) for s in sections]
            features.extend([
                len(sections),
                np.mean(section_durations),
                np.std(section_durations),
                np.min(section_durations),
                np.max(section_durations),
                0, 0, 0, 0, 0,
            ])
        else:
            features.extend([0] * 10)
        
        # Tempo features (10 dims)
        tempo_changes = audio_analysis.get("tempo_changes", [])
        features.extend([
            len(tempo_changes),
            0, 0, 0, 0, 0, 0, 0, 0, 0,
        ])
        
        # Duration and misc (15 dims)
        duration = audio_analysis.get("duration", 0)
        features.extend([
            duration / 300,  # Normalize to 5 min songs
            1 if duration < 60 else 0,  # Short
            1 if 60 <= duration < 180 else 0,  # Medium
            1 if duration >= 180 else 0,  # Long
            0, 0, 0, 0, 0, 0, 0, 0,  # Padding
        ])
        
        # Pad to 100 dims
        while len(features) < 100:
            features.append(0)
        
        return np.array(features[:100])

    @staticmethod
    def extract_for_star_rating(beatmap_features: Dict) -> np.ndarray:
        """Extract 50-dim feature vector for star rating prediction.
        
        Args:
            beatmap_features: Computed beatmap metrics
            
        Returns:
            50-dimensional feature vector
        """
        features = []
        
        # Spacing features (10 dims)
        features.extend([
            beatmap_features.get("avg_spacing", 100) / 300,
            beatmap_features.get("max_spacing", 200) / 400,
            beatmap_features.get("min_spacing", 50) / 200,
            (beatmap_features.get("max_spacing", 200) - beatmap_features.get("min_spacing", 50)) / 400,
            0, 0, 0, 0, 0, 0,
        ])
        
        # Density features (10 dims)
        features.extend([
            beatmap_features.get("object_density", 0.5),
            beatmap_features.get("circle_density", 0.3),
            beatmap_features.get("slider_density", 0.1),
            beatmap_features.get("stream_density", 0.1),
            0, 0, 0, 0, 0, 0,
        ])
        
        # Pattern features (10 dims)
        features.extend([
            beatmap_features.get("stream_length", 4) / 20,
            beatmap_features.get("jump_count", 0) / 50,
            beatmap_features.get("wiggle_count", 0) / 30,
            beatmap_features.get("slider_count", 0) / 100,
            0, 0, 0, 0, 0, 0,
        ])
        
        # Difficulty features (10 dims)
        features.extend([
            beatmap_features.get("peak_difficulty", 0.5),
            beatmap_features.get("avg_difficulty", 0.5),
            beatmap_features.get("difficulty_variance", 0.1),
            beatmap_features.get("stream_speed", 0.5),
            0, 0, 0, 0, 0, 0,
        ])
        
        # Pad to 50 dims
        while len(features) < 50:
            features.append(0)
        
        return np.array(features[:50])

    @staticmethod
    def extract_for_style_classification(hit_objects: List[Dict]) -> np.ndarray:
        """Extract variable-length sequence for style classification.
        
        Args:
            hit_objects: List of hit object data
            
        Returns:
            (n_timesteps, 20) feature matrix
        """
        if not hit_objects:
            return np.zeros((1, 20))
        
        features = []
        for i, obj in enumerate(hit_objects):
            obj_features = []
            
            # Position features
            obj_features.extend([
                obj.get("x", 256) / 512,
                obj.get("y", 192) / 384,
            ])
            
            # Timing features
            if i > 0:
                time_delta = (obj.get("time", 0) - hit_objects[i-1].get("time", 0)) / 100
                obj_features.append(time_delta)
            else:
                obj_features.append(0)
            
            # Spacing to previous
            if i > 0:
                dx = obj.get("x", 256) - hit_objects[i-1].get("x", 256)
                dy = obj.get("y", 192) - hit_objects[i-1].get("y", 192)
                spacing = np.sqrt(dx**2 + dy**2) / 300
                obj_features.append(spacing)
            else:
                obj_features.append(0)
            
            # Object type
            obj_type = obj.get("type", "circle")
            obj_features.extend([
                1 if obj_type == "circle" else 0,
                1 if obj_type == "slider" else 0,
                1 if obj_type == "spinner" else 0,
            ])
            
            # Pad to 20 dims
            while len(obj_features) < 20:
                obj_features.append(0)
            
            features.append(obj_features[:20])
        
        return np.array(features)


class MusicalFeatureExtractor:
    """Extract musical features for model input."""

    @staticmethod
    def extract_for_pattern_prediction(musical_features: Dict) -> np.ndarray:
        """Extract 30-dim musical feature vector.
        
        Args:
            musical_features: From MusicalFeatureExtractor
            
        Returns:
            30-dimensional feature vector
        """
        features = []
        
        # Kick features (6 dims)
        kicks = musical_features.get("kicks", [])
        if kicks:
            kick_times = np.array([k.time for k in kicks])
            kick_velocities = np.array([k.velocity for k in kicks])
            features.extend([
                len(kicks) / 100,  # Kick density
                np.mean(kick_velocities),
                np.std(kick_velocities),
                np.min(np.diff(kick_times)) if len(kick_times) > 1 else 0,
                np.max(np.diff(kick_times)) if len(kick_times) > 1 else 0,
                np.mean(np.diff(kick_times)) if len(kick_times) > 1 else 0,
            ])
        else:
            features.extend([0] * 6)
        
        # Snare features (6 dims)
        snares = musical_features.get("snares", [])
        if snares:
            snare_times = np.array([s.time for s in snares])
            snare_velocities = np.array([s.velocity for s in snares])
            features.extend([
                len(snares) / 100,
                np.mean(snare_velocities),
                np.std(snare_velocities),
                np.min(np.diff(snare_times)) if len(snare_times) > 1 else 0,
                np.max(np.diff(snare_times)) if len(snare_times) > 1 else 0,
                np.mean(np.diff(snare_times)) if len(snare_times) > 1 else 0,
            ])
        else:
            features.extend([0] * 6)
        
        # Vocal features (6 dims)
        vocals = musical_features.get("vocals", [])
        if vocals:
            vocal_times = np.array([v.time for v in vocals])
            vocal_velocities = np.array([v.velocity for v in vocals])
            features.extend([
                len(vocals) / 100,
                np.mean(vocal_velocities),
                np.std(vocal_velocities),
                np.mean([v.duration for v in vocals]),
                0, 0,
            ])
        else:
            features.extend([0] * 6)
        
        # Bass and Cymbal features (6 dims)
        bass = musical_features.get("bass", [])
        cymbals = musical_features.get("cymbals", [])
        features.extend([
            len(bass) / 100,
            np.mean([b.velocity for b in bass]) if bass else 0,
            len(cymbals) / 100,
            np.mean([c.velocity for c in cymbals]) if cymbals else 0,
            0, 0,
        ])
        
        # Pad to 30 dims
        while len(features) < 30:
            features.append(0)
        
        return np.array(features[:30])
