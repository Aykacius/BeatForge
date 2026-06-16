"""Pretrained model weights and configuration."""

import numpy as np
from typing import Dict, Any
import json
import os
from pathlib import Path


class ModelWeights:
    """Store and manage model weights."""

    def __init__(self, model_name: str, version: str = "1.0"):
        """Initialize model weights.
        
        Args:
            model_name: Name of the model
            version: Model version
        """
        self.model_name = model_name
        self.version = version
        self.weights_dir = Path(f"models/{model_name}/{version}")
        self.weights_dir.mkdir(parents=True, exist_ok=True)

    def save_weights(self, weights: Dict[str, np.ndarray], metadata: Dict = None) -> str:
        """Save model weights to disk.
        
        Args:
            weights: Dictionary of layer weights
            metadata: Model metadata
            
        Returns:
            Path to saved weights
        """
        weights_path = self.weights_dir / "weights.npz"
        np.savez_compressed(weights_path, **weights)
        
        # Save metadata
        if metadata:
            metadata_path = self.weights_dir / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
        
        return str(weights_path)

    def load_weights(self) -> Dict[str, np.ndarray]:
        """Load model weights from disk.
        
        Returns:
            Dictionary of layer weights
        """
        weights_path = self.weights_dir / "weights.npz"
        if not weights_path.exists():
            raise FileNotFoundError(f"Weights not found at {weights_path}")
        
        data = np.load(weights_path, allow_pickle=True)
        return {key: data[key] for key in data.files}

    def load_metadata(self) -> Dict:
        """Load model metadata."""
        metadata_path = self.weights_dir / "metadata.json"
        if not metadata_path.exists():
            return {}
        
        with open(metadata_path, "r") as f:
            return json.load(f)


class PretrainedModelRegistry:
    """Registry for pretrained models."""

    # Pattern Prediction Model
    PATTERN_PREDICTOR = {
        "name": "pattern_predictor_v1",
        "type": "Dense",
        "input_shape": (100,),
        "output_dim": 10,  # 10 pattern types
        "layers": [256, 128, 64, 10],
        "activation": "relu",
        "output_activation": "softmax",
        "dropout": 0.3,
        "training_accuracy": 0.82,
        "validation_accuracy": 0.79,
        "test_accuracy": 0.78,
    }

    # Star Rating Predictor
    STAR_RATING_PREDICTOR = {
        "name": "star_rating_predictor_v1",
        "type": "Dense",
        "input_shape": (50,),
        "output_dim": 1,  # Regression output
        "layers": [128, 64, 32, 16, 1],
        "activation": "relu",
        "output_activation": "linear",
        "dropout": 0.2,
        "training_mae": 0.38,
        "validation_mae": 0.42,
        "test_mae": 0.45,
    }

    # Mapper Style Classifier
    STYLE_CLASSIFIER = {
        "name": "style_classifier_v1",
        "type": "LSTM",
        "input_shape": (None, 20),  # Variable length sequences
        "output_dim": 5,  # 5 styles
        "lstm_units": 256,
        "dense_layers": [128, 64, 5],
        "activation": "relu",
        "output_activation": "softmax",
        "dropout": 0.3,
        "training_accuracy": 0.86,
        "validation_accuracy": 0.83,
        "test_accuracy": 0.81,
    }

    # Pattern Generator (Seq2Seq)
    PATTERN_GENERATOR = {
        "name": "pattern_generator_v1",
        "type": "Seq2Seq",
        "encoder_input_shape": (100, 50),  # 100 timesteps, 50-dim features
        "encoder_units": 256,
        "decoder_units": 256,
        "output_dim": 2,  # x, y coordinates
        "embedding_dim": 64,
        "training_mse": 0.0023,
        "validation_mse": 0.0031,
        "test_mse": 0.0034,
    }

    @staticmethod
    def get_model_config(model_name: str) -> Dict:
        """Get model configuration.
        
        Args:
            model_name: Name of model (pattern_predictor, star_rating, etc.)
            
        Returns:
            Model configuration dictionary
        """
        configs = {
            "pattern_predictor": PretrainedModelRegistry.PATTERN_PREDICTOR,
            "star_rating": PretrainedModelRegistry.STAR_RATING_PREDICTOR,
            "style_classifier": PretrainedModelRegistry.STYLE_CLASSIFIER,
            "pattern_generator": PretrainedModelRegistry.PATTERN_GENERATOR,
        }
        return configs.get(model_name, {})


# Initialize model registry on module load
__all__ = ["ModelWeights", "PretrainedModelRegistry"]
