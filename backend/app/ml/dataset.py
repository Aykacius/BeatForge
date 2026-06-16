"""Machine learning dataset and model architecture."""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime


@dataclass
class BeatmapSample:
    """A single training sample (audio + beatmap)."""
    audio_id: str
    audio_path: str
    audio_features: Dict  # From AudioAnalyzer
    musical_features: Dict  # From MusicalFeatureExtractor
    beatmap_path: str
    hit_objects: List[Dict]  # Flattened hit object data
    difficulty: str
    mapping_style: str
    star_rating: float
    creator: str  # Human mapper who created it
    metadata: Dict  # Additional context
    quality_score: float  # 0-1 rating of map quality
    popularity: int  # Download count, favorites, etc.

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "audio_id": self.audio_id,
            "audio_path": self.audio_path,
            "audio_features": self.audio_features,
            "musical_features": self.musical_features,
            "beatmap_path": self.beatmap_path,
            "hit_objects": self.hit_objects,
            "difficulty": self.difficulty,
            "mapping_style": self.mapping_style,
            "star_rating": self.star_rating,
            "creator": self.creator,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "popularity": self.popularity,
        }


class BeatmapDataset:
    """Dataset management for training."""

    def __init__(self, dataset_path: str = "datasets/beatmaps"):
        """Initialize dataset.
        
        Args:
            dataset_path: Root directory for dataset
        """
        self.dataset_path = dataset_path
        self.samples: List[BeatmapSample] = []

    def add_sample(self, sample: BeatmapSample) -> None:
        """Add a sample to the dataset."""
        self.samples.append(sample)

    def save(self, path: str) -> None:
        """Save dataset to JSON file."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "num_samples": len(self.samples),
            "samples": [s.to_dict() for s in self.samples],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> None:
        """Load dataset from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        
        self.samples = [BeatmapSample(**s) for s in data["samples"]]

    def get_statistics(self) -> Dict:
        """Get dataset statistics."""
        if not self.samples:
            return {}
        
        difficulties = {}
        styles = {}
        star_ratings = []
        quality_scores = []
        
        for sample in self.samples:
            difficulties[sample.difficulty] = difficulties.get(sample.difficulty, 0) + 1
            styles[sample.mapping_style] = styles.get(sample.mapping_style, 0) + 1
            star_ratings.append(sample.star_rating)
            quality_scores.append(sample.quality_score)
        
        import numpy as np
        return {
            "num_samples": len(self.samples),
            "difficulties": difficulties,
            "styles": styles,
            "star_rating_range": (min(star_ratings), max(star_ratings)),
            "star_rating_mean": float(np.mean(star_ratings)),
            "quality_score_mean": float(np.mean(quality_scores)),
        }


class PatternDataset:
    """Dataset for pattern prediction models."""

    def __init__(self):
        """Initialize pattern dataset."""
        self.patterns: List[Dict] = []

    def add_pattern(self, context: Dict, pattern: List[Tuple[float, float]], label: str) -> None:
        """Add a pattern with context.
        
        Args:
            context: Audio context (section, energy, BPM, etc.)
            pattern: List of (x, y) positions
            label: Pattern type label (stream, jump, etc.)
        """
        self.patterns.append({
            "context": context,
            "pattern": pattern,
            "label": label,
        })

    def get_by_label(self, label: str) -> List[Dict]:
        """Get patterns by type."""
        return [p for p in self.patterns if p["label"] == label]


# Model Architecture Templates

class ModelArchitecture:
    """Base architecture for ML models."""

    @staticmethod
    def pattern_prediction_cnn():
        """CNN for pattern prediction from audio features.
        
        Input: Audio features (100-dim)
        Output: Pattern type probabilities (10 classes)
        """
        return {
            "name": "PatternPredictionCNN",
            "architecture": [
                {"type": "Dense", "units": 256, "activation": "relu"},
                {"type": "BatchNorm"},
                {"type": "Dropout", "rate": 0.3},
                {"type": "Dense", "units": 128, "activation": "relu"},
                {"type": "BatchNorm"},
                {"type": "Dropout", "rate": 0.2},
                {"type": "Dense", "units": 64, "activation": "relu"},
                {"type": "Dense", "units": 10, "activation": "softmax"},  # Pattern classes
            ],
            "input_shape": (100,),
            "loss": "categorical_crossentropy",
            "metrics": ["accuracy"],
        }

    @staticmethod
    def star_rating_predictor():
        """Neural network for star rating prediction.
        
        Input: Beatmap features (spacing, density, patterns, etc.)
        Output: Star rating 2.0-9.0
        """
        return {
            "name": "StarRatingPredictor",
            "architecture": [
                {"type": "Dense", "units": 128, "activation": "relu"},
                {"type": "Dropout", "rate": 0.2},
                {"type": "Dense", "units": 64, "activation": "relu"},
                {"type": "Dense", "units": 32, "activation": "relu"},
                {"type": "Dense", "units": 1, "activation": "linear"},  # Regression output
            ],
            "input_shape": (50,),
            "loss": "mse",
            "metrics": ["mae"],
        }

    @staticmethod
    def mapper_style_classifier():
        """Classify beatmap style (tech, jump, aim, etc.).
        
        Input: Beatmap pattern sequences (variable length)
        Output: Style probabilities (5 classes)
        """
        return {
            "name": "MapperStyleClassifier",
            "architecture": [
                {"type": "LSTM", "units": 256, "return_sequences": True},
                {"type": "Dropout", "rate": 0.3},
                {"type": "LSTM", "units": 128},
                {"type": "Dense", "units": 64, "activation": "relu"},
                {"type": "Dense", "units": 5, "activation": "softmax"},  # Style classes
            ],
            "input_shape": (None, 20),  # Variable length sequences of 20-dim features
            "loss": "categorical_crossentropy",
            "metrics": ["accuracy"],
        }

    @staticmethod
    def sequence_to_sequence_generator():
        """Seq2seq model for pattern generation.
        
        Encoder: Audio features
        Decoder: Generate hit object coordinates
        """
        return {
            "name": "Seq2SeqPatternGenerator",
            "encoder": {
                "type": "LSTM",
                "units": 256,
                "input_shape": (100, 50),  # 100 timesteps of 50-dim features
            },
            "decoder": {
                "type": "LSTM",
                "units": 256,
                "layers": 2,
            },
            "output_layer": {
                "type": "Dense",
                "units": 2,  # x, y coordinates
            },
            "loss": "mse",
        }

    @staticmethod
    def attention_mapper():
        """Attention-based mapper that focuses on important audio events."""
        return {
            "name": "AttentionMapper",
            "components": {
                "audio_encoder": {
                    "type": "Conv1D",
                    "filters": 64,
                    "kernel_size": 3,
                    "layers": 3,
                },
                "attention": {
                    "type": "MultiHeadAttention",
                    "num_heads": 8,
                    "key_dim": 64,
                },
                "pattern_decoder": {
                    "type": "LSTM",
                    "units": 256,
                },
            },
            "loss": "mse",
        }
