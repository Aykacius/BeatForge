"""Training data preparation and utilities."""

import os
from pathlib import Path
import numpy as np
from typing import List, Tuple, Dict
from loguru import logger


class DatasetBuilder:
    """Build and manage training datasets."""

    def __init__(self, data_dir: str = "datasets"):
        """Initialize dataset builder.
        
        Args:
            data_dir: Root directory for datasets
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.patterns_dir = self.data_dir / "patterns"
        self.beatmaps_dir = self.data_dir / "beatmaps"
        self.patterns_dir.mkdir(exist_ok=True)
        self.beatmaps_dir.mkdir(exist_ok=True)

    def save_training_batch(
        self,
        name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
    ) -> str:
        """Save training batch to disk.
        
        Args:
            name: Dataset name
            X_train, y_train: Training data
            X_val, y_val: Validation data
            
        Returns:
            Path to saved dataset
        """
        dataset_path = self.data_dir / f"{name}.npz"
        
        np.savez_compressed(
            dataset_path,
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
        )
        
        logger.info(f"Saved dataset to {dataset_path}")
        return str(dataset_path)

    def load_training_batch(self, name: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load training batch from disk.
        
        Args:
            name: Dataset name
            
        Returns:
            Tuple of (X_train, y_train, X_val, y_val)
        """
        dataset_path = self.data_dir / f"{name}.npz"
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        data = np.load(dataset_path, allow_pickle=True)
        return data["X_train"], data["y_train"], data["X_val"], data["y_val"]


class DataSplitter:
    """Split data for training, validation, and testing."""

    @staticmethod
    def train_val_test_split(
        X: np.ndarray,
        y: np.ndarray,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        shuffle: bool = True,
        random_state: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into train/val/test sets.
        
        Args:
            X, y: Features and labels
            train_ratio, val_ratio, test_ratio: Split ratios
            shuffle: Whether to shuffle data
            random_state: Random seed
            
        Returns:
            Tuple of (X_train, y_train, X_val, y_val, X_test, y_test)
        """
        if shuffle:
            np.random.seed(random_state)
            indices = np.random.permutation(len(X))
            X = X[indices]
            y = y[indices]
        
        n = len(X)
        train_idx = int(n * train_ratio)
        val_idx = train_idx + int(n * val_ratio)
        
        X_train, y_train = X[:train_idx], y[:train_idx]
        X_val, y_val = X[train_idx:val_idx], y[train_idx:val_idx]
        X_test, y_test = X[val_idx:], y[val_idx:]
        
        return X_train, y_train, X_val, y_val, X_test, y_test

    @staticmethod
    def k_fold_split(
        X: np.ndarray,
        y: np.ndarray,
        k: int = 5,
        random_state: int = 42,
    ) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """K-fold cross-validation split.
        
        Args:
            X, y: Features and labels
            k: Number of folds
            random_state: Random seed
            
        Returns:
            List of (X_train, y_train, X_val, y_val) tuples
        """
        np.random.seed(random_state)
        indices = np.random.permutation(len(X))
        
        fold_size = len(X) // k
        folds = []
        
        for i in range(k):
            val_start = i * fold_size
            val_end = val_start + fold_size if i < k - 1 else len(X)
            
            val_indices = indices[val_start:val_end]
            train_indices = np.concatenate([indices[:val_start], indices[val_end:]])
            
            X_train, y_train = X[train_indices], y[train_indices]
            X_val, y_val = X[val_indices], y[val_indices]
            
            folds.append((X_train, y_train, X_val, y_val))
        
        return folds


class MetricsCalculator:
    """Calculate training and evaluation metrics."""

    @staticmethod
    def classification_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict:
        """Calculate classification metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_true, y_pred)
        
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "confusion_matrix": cm.tolist(),
        }

    @staticmethod
    def regression_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict:
        """Calculate regression metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        return {
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae),
            "r2_score": float(r2),
        }
