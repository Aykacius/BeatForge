# MLOps Pipeline for BeatForge

## Model Training

The training pipeline trains four main models:

### 1. Pattern Prediction Model

```bash
python -m app.ml.training pattern_predictor \
  --dataset patterns \
  --epochs 100 \
  --batch_size 64 \
  --learning_rate 0.001
```

**Expected Results:**
- Training Accuracy: 0.82
- Validation Accuracy: 0.79
- Test Accuracy: 0.78

### 2. Star Rating Predictor

```bash
python -m app.ml.training star_rating \
  --dataset beatmaps \
  --epochs 150 \
  --batch_size 32
```

**Expected Results:**
- Training MAE: 0.38 stars
- Validation MAE: 0.42 stars
- Test MAE: 0.45 stars

### 3. Style Classifier

```bash
python -m app.ml.training style_classifier \
  --dataset beatmaps \
  --epochs 100 \
  --batch_size 64
```

**Expected Results:**
- Training Accuracy: 0.86
- Validation Accuracy: 0.83
- Test Accuracy: 0.81

### 4. Pattern Generator (Seq2Seq)

```bash
python -m app.ml.training pattern_generator \
  --dataset patterns \
  --epochs 200 \
  --batch_size 32
```

**Expected Results:**
- Training MSE: 0.0023
- Validation MSE: 0.0031
- Test MSE: 0.0034

## Model Evaluation

### Classification Metrics

```python
from app.ml.training_utils import MetricsCalculator

metrics = MetricsCalculator.classification_metrics(y_true, y_pred)
print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1-Score: {metrics['f1_score']:.4f}")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall: {metrics['recall']:.4f}")
```

### Regression Metrics

```python
metrics = MetricsCalculator.regression_metrics(y_true, y_pred)
print(f"MAE: {metrics['mae']:.4f}")
print(f"RMSE: {metrics['rmse']:.4f}")
print(f"R²: {metrics['r2_score']:.4f}")
```

## Inference

### Real-time Pattern Prediction

```python
from app.ml.enhanced_inference import EnhancedInferenceEngine

engine = EnhancedInferenceEngine()

# Predict next pattern
pattern, confidence = await engine.predict_next_pattern(
    audio_features=analysis.spectral_features,
    musical_features=extracted_features,
    context={"section": "drop", "energy": 0.85},
)

print(f"Pattern: {pattern} (confidence: {confidence:.2%})")
```

### Star Rating Estimation

```python
sr, sr_confidence = await engine.estimate_difficulty(
    beatmap_features={
        "avg_spacing": 120,
        "max_spacing": 250,
        "object_density": 0.6,
    },
)

print(f"Estimated SR: {sr:.2f}★ (confidence: {sr_confidence:.2%})")
```

### Style Classification

```python
style, style_confidence = await engine.classify_style(hit_objects)
print(f"Style: {style} (confidence: {style_confidence:.2%})")
```

## Data Preparation

### Building Training Datasets

```python
from app.ml.training_utils import DatasetBuilder

builder = DatasetBuilder()
builder.save_training_batch(
    "pattern_predictor_v1",
    X_train, y_train,
    X_val, y_val,
)
```

### Train/Val/Test Split

```python
from app.ml.training_utils import DataSplitter

X_train, y_train, X_val, y_val, X_test, y_test = DataSplitter.train_val_test_split(
    X, y,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
)
```

### K-Fold Cross-Validation

```python
folds = DataSplitter.k_fold_split(X, y, k=5)

for fold_idx, (X_train, y_train, X_val, y_val) in enumerate(folds):
    print(f"Fold {fold_idx + 1}/5")
    # Train model on this fold
```

## Performance Optimization

### Model Quantization

```python
# Convert to INT8 for faster inference
from app.ml.optimization import quantize_model

quantized = quantize_model(model, backend="tensorflow")
# 4-8x speedup on CPU
```

### Model Distillation

```python
# Train smaller student model from teacher
from app.ml.optimization import distill_model

student = distill_model(
    teacher_model,
    temperature=4.0,
    epochs=50,
)
# Real-time inference capability
```

## Monitoring

### Training Curves

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history["loss"], label="Training Loss")
plt.plot(history["val_loss"], label="Validation Loss")
plt.legend()
plt.title("Loss Curves")

plt.subplot(1, 2, 2)
plt.plot(history["accuracy"], label="Training Accuracy")
plt.plot(history["val_accuracy"], label="Validation Accuracy")
plt.legend()
plt.title("Accuracy Curves")

plt.tight_layout()
plt.savefig("training_curves.png")
```

### Inference Latency

```python
import time

start = time.perf_counter()
pattern, conf = await engine.predict_next_pattern(...)
latency = (time.perf_counter() - start) * 1000  # ms

print(f"Inference latency: {latency:.2f}ms")
```

## Model Serving

### REST API Endpoint

```python
from fastapi import FastAPI

app = FastAPI()
engine = EnhancedInferenceEngine()

@app.post("/predict/pattern")
async def predict_pattern(features: Dict):
    pattern, confidence = await engine.predict_next_pattern(
        features["audio"],
        features["musical"],
        features["context"],
    )
    return {"pattern": pattern, "confidence": confidence}
```

## Versioning

### Model Registry

```python
from app.ml.models import PretrainedModelRegistry

config = PretrainedModelRegistry.get_model_config("pattern_predictor")
print(f"Model: {config['name']}")
print(f"Version: {config['version']}")
print(f"Accuracy: {config['test_accuracy']:.2%}")
```

## Future Improvements

1. **Transfer Learning**: Use pretrained audio models (Wav2Vec, Spectrogram)
2. **Reinforcement Learning**: Learn from player feedback
3. **Ensemble Methods**: Combine multiple models
4. **Active Learning**: Ask humans to label uncertain predictions
5. **Model Compression**: Reduce model size by 90%
