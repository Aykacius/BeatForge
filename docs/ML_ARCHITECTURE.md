# BeatForge - Machine Learning Architecture

## Overview

The ML system is designed to learn from expert beatmaps and improve pattern generation over time.

## Training Pipeline

```
Human Beatmaps
       ↓
[Feature Extraction]
  ├─ Audio Analysis
  ├─ Musical Features
  └─ Beatmap Metrics
       ↓
[Dataset Creation]
  ├─ Pattern Dataset
  ├─ Star Rating Dataset
  └─ Style Dataset
       ↓
[Model Training]
  ├─ Pattern Predictor (CNN/LSTM)
  ├─ Star Rating Predictor (Regression)
  └─ Mapper Style Classifier
       ↓
[Inference]
  ├─ Real-time predictions
  └─ Beatmap generation
```

## Models

### 1. Pattern Prediction Model

**Input**: Audio context (BPM, energy, section, musical features)
**Output**: Pattern type probabilities (stream, jump, wiggle, etc.)
**Architecture**: 3-layer Dense NN or LSTM
**Training Data**: 10,000+ beatmap patterns with labels
**Expected Accuracy**: 75-85%

### 2. Star Rating Predictor

**Input**: Beatmap metrics (spacing, density, patterns, object count)
**Output**: Predicted star rating (2.0-9.0)
**Architecture**: Regression network
**Training Data**: 5,000+ ranked beatmaps
**Expected MAE**: ±0.5 stars

### 3. Mapper Style Classifier

**Input**: Sequence of patterns
**Output**: Style probabilities (Tech, Jump, Aim, Hybrid, Stream Practice)
**Architecture**: LSTM with attention
**Training Data**: 3,000+ labeled beatmaps
**Expected Accuracy**: 80-90%

### 4. Seq2Seq Pattern Generator

**Input**: Audio features (100 timesteps)
**Output**: Hit object coordinates (variable length)
**Architecture**: Encoder-Decoder LSTM
**Training Data**: 50,000+ patterns
**Expected Performance**: Visual similarity to human patterns

## Dataset Management

### BeatmapSample

Each training sample contains:
- Audio file reference
- Extracted audio features (BPM, beats, onsets, etc.)
- Musical features (kicks, snares, vocals, etc.)
- Beatmap file (.osu)
- Hit objects (flattened coordinates and timings)
- Difficulty level
- Mapping style
- Star rating
- Creator info
- Quality score (human rating)
- Popularity metrics

### Dataset Statistics

Target dataset composition:
- **Total samples**: 100,000+
- **Difficulties**: 5 (Easy, Normal, Hard, Insane, Expert+)
- **Styles**: 5 (Tech, Jump, Aim, Hybrid, Stream Practice)
- **Star rating range**: 2.0-9.0 stars
- **Quality threshold**: 7.0+ quality score

## Training Workflow

### Phase 1: Data Collection

1. Scrape ranked beatmaps from osu! database
2. Extract audio features using librosa
3. Parse .osu files and extract hit objects
4. Compute difficulty metrics
5. Filter for quality (remove spam/low-quality maps)

### Phase 2: Feature Engineering

1. Normalize audio features (0-1 range)
2. Encode categorical features (difficulty, style)
3. Compute statistical features (mean, std, percentiles)
4. Create time-based windows
5. Generate context features

### Phase 3: Model Training

```python
from app.ml.inference import ModelTrainer, TrainingConfig

config = TrainingConfig(
    model_type="pattern_predictor",
    batch_size=64,
    epochs=100,
    learning_rate=0.001,
    validation_split=0.2,
    early_stopping_patience=15,
)

trainer = ModelTrainer(config)
history = await trainer.train(X_train, y_train, X_val, y_val)
```

### Phase 4: Evaluation

Metrics tracked:
- Accuracy / MAE
- F1-score (per class)
- Confusion matrix
- Cross-validation score
- Inference time

### Phase 5: Deployment

1. Save model weights
2. Package with tokenizer/scaler
3. Deploy to inference engine
4. Monitor performance
5. Collect user feedback for retraining

## Feature Vectors

### Audio Features (50-dim)
```python
[
    bpm,                    # 0
    avg_beat_energy,        # 1
    std_beat_energy,        # 2
    onset_density,          # 3
    spectral_centroid,      # 4
    spectral_rolloff,       # 5
    zero_crossing_rate,     # 6
    # ... 44 more
]
```

### Musical Features (30-dim)
```python
[
    kick_density,           # 0
    snare_density,          # 1
    cymbal_density,         # 2
    vocal_energy,           # 3
    bass_activity,          # 4
    # ... 25 more
]
```

### Beatmap Features (25-dim)
```python
[
    avg_spacing,            # 0
    max_spacing,            # 1
    stream_length,          # 2
    jump_count,             # 3
    object_density,         # 4
    # ... 20 more
]
```

## Inference

### Runtime Prediction

During beatmap generation:

```python
engine = InferenceEngine()

# Predict next pattern
pattern_type, confidence = await engine.predict_next_pattern(
    audio_features=analysis.spectral_features,
    musical_features=extracted_features,
    context={"section": "drop", "difficulty": 4},
)

# Estimate final difficulty
sr_pred, sr_confidence = await engine.estimate_difficulty(
    beatmap_metrics={...},
)
```

## Performance Optimization

### Model Quantization
- Convert to FP16 / INT8 for faster inference
- 4-8x speedup with minimal accuracy loss

### Model Distillation
- Train smaller student model from large teacher
- Real-time inference on CPU

### Caching
- Cache predictions for identical contexts
- Batch predictions when possible

## Future Enhancements

### 1. Transfer Learning
- Use pretrained audio models (Wav2Vec, Spectrogram)
- Fine-tune on beatmap patterns
- Reduce training data requirement

### 2. Reinforcement Learning
- Reward model for playability
- Learn from player feedback (cleared, failed, favorites)
- Optimize for specific player preferences

### 3. Generative Models
- VAE for pattern generation
- GAN for beatmap synthesis
- Diffusion models for iterative refinement

### 4. Explainability
- SHAP values for feature importance
- Attention visualization
- Pattern similarity analysis

## Research Papers

Inspired by:
- "Audio Tagging with Connectionist Temporal Classification Model" (audioset-style labeling)
- "Learning to Compose Domain-Specific Languages" (pattern grammars)
- "Sequence to Sequence Learning with Neural Networks" (Sutskever et al.)
