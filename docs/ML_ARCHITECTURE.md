# ML Architecture

## Overview

The ML system is designed to progressively improve beatmap generation quality through three complementary models:

1. **Pattern Prediction Model** - Recommends optimal pattern types for audio contexts
2. **Star Rating Predictor** - Estimates difficulty of generated beatmaps
3. **Style Classifier** - Identifies and replicates mapper styles

## System Architecture

```
Audio Features
    ↓
┌───────────────────────────────────────┐
│     Feature Extraction Pipeline       │
├───────────────────────────────────────┤
│ • Onset strength                      │
│ • Energy contours                     │
│ • Spectral features (MFCC, centroids) │
│ • Harmonic/percussive separation      │
│ • Chroma features                     │
└────────┬────────────────────────────┬─┘
         ↓                            ↓
┌─────────────────────┐    ┌──────────────────────┐
│ Pattern Predictor   │    │ Star Rating Predictor │
├─────────────────────┤    ├──────────────────────┤
│ Input: Features     │    │ Input: Beatmap data  │
│ Output: P(pattern)  │    │ Output: Est. stars   │
└────────┬────────────┘    └──────────┬───────────┘
         ↓                            ↓
┌─────────────────────────────────────────┐
│     Mapping Engine (Decision Layer)     │
├─────────────────────────────────────────┤
│ Selects patterns based on:              │
│ • ML predictions + confidence           │
│ • Difficulty parameters                 │
│ • Cursor momentum constraints           │
│ • Recent pattern history                │
└─────────────┬───────────────────────────┘
              ↓
         Generated Beatmap
              ↓
         User Feedback Collection
              ↓
         Model Retraining
```

## Model Specifications

### 1. Pattern Prediction Model

**Purpose**: For each beat/onset, predict the most likely pattern type

**Input Features**:
- Onset strength (probability of attack)
- Local energy level (quiet vs loud)
- Energy derivative (is volume increasing?)
- Spectral centroid (brightness)
- MFCC values (12 coefficients)
- Tempo/BPM context
- Section type (intro/verse/drop)
- Recent pattern history (last 5 patterns)

**Output**: Probability distribution over pattern classes
```
{
  "circle": 0.45,
  "stream": 0.25,
  "burst": 0.15,
  "jump": 0.10,
  "slider": 0.05
}
```

**Architecture**:
```
Input Layer (50 features)
    ↓
Dense(128, ReLU) + Dropout(0.3)
    ↓
Dense(64, ReLU) + Dropout(0.3)
    ↓
Dense(32, ReLU)
    ↓
Output Layer (5 classes, Softmax)
```

**Training Data**:
- 10,000+ hand-mapped beatmaps from osu!
- Extract pattern type for each object
- Compute audio features for corresponding beats
- Split: 80% train, 10% val, 10% test

**Metrics**:
- Accuracy: Target > 75%
- F1-score per class
- Confusion matrix analysis
- Real-time inference latency: < 5ms per beat

**Deployment**:
- ONNX format for production
- Quantization for 50% size reduction
- Batch inference during generation

---

### 2. Star Rating Predictor

**Purpose**: Estimate difficulty (star rating) of generated beatmaps

**Input Features**:
- Object count
- Circle/slider/spinner counts
- Average spacing between objects
- Average object density (objects/second)
- Max stream length
- Max jump distance
- Average slider complexity
- BPM
- Section patterns

**Output**: Estimated star rating (2.0 - 9.0)

**Architecture**:
```
Input Layer (15 features)
    ↓
Dense(64, ReLU) + Dropout(0.2)
    ↓
Dense(32, ReLU) + Dropout(0.2)
    ↓
Output Layer (1 neuron, Linear activation)
```

**Training Data**:
- 50,000+ ranked beatmaps from osu!
- Use official star rating as ground truth
- Feature engineering from .osu files
- Split: 80% train, 10% val, 10% test

**Loss Function**: Mean Squared Error (MSE)
```
Loss = MSE(predicted_rating, official_rating)
```

**Metrics**:
- MAE (Mean Absolute Error): Target < 0.5 stars
- R² score: Target > 0.85
- Residual analysis by difficulty band

**Usage in Generation**:
```python
# Generate initial beatmap
generated_map = mapping_engine.generate(audio_features, difficulty)

# Predict star rating
predicted_stars = star_predictor.predict(generated_map)

# If too high/low, adjust parameters
if predicted_stars > target_stars + 0.5:
    # Reduce difficulty
    difficulty_manager.decrease_spacing()
    generated_map = mapping_engine.regenerate()
elif predicted_stars < target_stars - 0.5:
    # Increase difficulty
    difficulty_manager.increase_density()
    generated_map = mapping_engine.regenerate()
```

---

### 3. Style Classifier

**Purpose**: Identify mapping style and generate maps in selected style

**Styles**:
1. **Technical Stream** - Precise aim, fast streams, varied angles
2. **Jump** - Large spacing, quick directional changes
3. **Hybrid** - Mix of streams and jumps
4. **Aim** - Large jumps, challenging angles
5. **Stream Practice** - Long consistent streams

**Input Features**:
- Pattern distribution (% streams, jumps, etc.)
- Average cursor movement angle changes
- Spacing distribution histogram
- Object density distribution
- Slider usage percentage
- BPM-adjusted speed metrics

**Architecture**: Multi-class classifier
```
Input Layer (20 features)
    ↓
Dense(128, ReLU) + Dropout(0.3)
    ↓
Dense(64, ReLU) + Dropout(0.3)
    ↓
Output Layer (5 classes, Softmax)
```

**Training Data**:
- 5,000+ beatmaps labeled by style (community voting)
- Extract style-specific features
- Data augmentation through variations

**Metrics**:
- Multi-class accuracy: Target > 70%
- Per-class precision and recall
- Confusion matrix for style similarity

**Usage in Generation**:
```python
# If user selects style
if user_selected_style:
    style_weights = style_classifier.get_style_weights(user_selected_style)
    pattern_predictor.apply_style_bias(style_weights)
    # This modifies the output probability distribution
    # E.g., for "Technical Stream": boost stream probability
```

---

## Feature Engineering Pipeline

### Audio Feature Extraction

```python
def extract_audio_features(audio_path: str) -> np.ndarray:
    """
    Extract ML-ready features from audio file.
    
    Returns shape (n_frames, n_features)
    """
    y, sr = librosa.load(audio_path)
    
    # Onset strength for attack detection
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Energy in multiple frequency bands
    S = np.abs(librosa.stft(y))
    energy_db = librosa.power_to_db(S, ref=np.max)
    
    # Spectral features
    spectral_centroid = librosa.feature.spectral_centroid(S=S)[0]
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=12)
    
    # Chroma (harmonic content)
    chroma = librosa.feature.chroma_stft(S=S)[0]
    
    # Tempogram for rhythm
    tempogram = librosa.feature.tempogram(y=y, sr=sr)
    
    # Harmonics vs percussive separation
    S_h, S_p = librosa.decompose.hpss(S)
    
    # Concatenate all features
    features = np.vstack([
        onset_env,
        energy_db.mean(axis=0),
        spectral_centroid,
        mfcc,
        chroma,
        tempogram.mean(axis=0)
    ])
    
    return features
```

### Beatmap Feature Extraction

```python
def extract_beatmap_features(beatmap: Beatmap) -> dict:
    """
    Extract features from a beatmap for difficulty prediction.
    """
    objects = beatmap.hit_objects
    
    features = {
        'total_objects': len(objects),
        'circle_count': sum(1 for o in objects if isinstance(o, Circle)),
        'slider_count': sum(1 for o in objects if isinstance(o, Slider)),
        'spinner_count': sum(1 for o in objects if isinstance(o, Spinner)),
        
        'avg_spacing': np.mean([distance(objects[i], objects[i+1]) 
                                for i in range(len(objects)-1)]),
        'max_spacing': np.max([distance(objects[i], objects[i+1]) 
                               for i in range(len(objects)-1)]),
        
        'object_density': len(objects) / beatmap.total_time,
        'avg_stream_length': calculate_avg_stream_length(objects),
        
        'bpm': beatmap.bpm,
        'drain_time': beatmap.drain_time,
    }
    
    return features
```

## Training Pipeline

### Data Collection

```python
# Collect from official osu! API
from datetime import datetime

def collect_training_data():
    """
    Collect ranked beatmaps for training.
    """
    for beatmap_id in get_ranked_beatmaps(mode='osu', status='ranked'):
        try:
            # Download beatmap
            beatmap_data = download_beatmap(beatmap_id)
            audio_path = extract_audio(beatmap_data)
            
            # Extract features
            audio_features = extract_audio_features(audio_path)
            beatmap_features = extract_beatmap_features(beatmap_data)
            
            # Store in database
            store_training_sample(
                audio_features=audio_features,
                beatmap_features=beatmap_features,
                star_rating=beatmap_data.stars,
                style=classify_style(beatmap_data),
                patterns=extract_patterns(beatmap_data)
            )
        except Exception as e:
            log_error(f"Failed to process {beatmap_id}: {e}")
```

### Model Training

```python
from tensorflow import keras
import numpy as np

def train_pattern_predictor():
    """
    Train pattern prediction model.
    """
    # Load training data
    X_train, y_train = load_training_data('pattern_predictor')
    X_val, y_val = load_validation_data('pattern_predictor')
    
    # Build model
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(5, activation='softmax')
    ])
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.F1Score(average='weighted')]
    )
    
    # Train with early stopping
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=[
            keras.callbacks.EarlyStopping(monitor='val_loss', patience=10),
            keras.callbacks.ModelCheckpoint('best_model.h5', monitor='val_accuracy'),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
        ]
    )
    
    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {test_acc:.4f}")
```

### Model Validation

```python
def validate_models():
    """
    Comprehensive validation of all ML models.
    """
    results = {}
    
    # Pattern predictor validation
    pattern_acc = evaluate_pattern_predictor(test_set)
    results['pattern_accuracy'] = pattern_acc
    
    # Star rating predictor validation
    rating_mae = evaluate_star_predictor(test_set)
    results['rating_mae'] = rating_mae
    
    # Style classifier validation
    style_acc = evaluate_style_classifier(test_set)
    results['style_accuracy'] = style_acc
    
    # Log results
    log_validation(results)
    
    # Return True if all metrics pass thresholds
    return (
        pattern_acc > 0.75 and
        rating_mae < 0.5 and
        style_acc > 0.70
    )
```

## Integration with Mapping Engine

### Pattern Selection

```python
def select_pattern(audio_context: dict, cursor_state: CursorState) -> str:
    """
    Select pattern type using ML predictions and constraints.
    """
    # Get ML predictions
    predictions = pattern_predictor.predict(audio_context)
    
    # Filter based on constraints
    valid_patterns = []
    for pattern_type, probability in predictions.items():
        if is_valid_pattern(pattern_type, cursor_state, audio_context):
            valid_patterns.append((pattern_type, probability))
    
    # Select with probability weighting
    selected = random.choices(
        [p[0] for p in valid_patterns],
        weights=[p[1] for p in valid_patterns]
    )[0]
    
    return selected
```

### Difficulty Adjustment

```python
def adjust_for_target_difficulty(beatmap: Beatmap, target_stars: float) -> Beatmap:
    """
    Iteratively adjust beatmap to hit target difficulty.
    """
    max_iterations = 3
    tolerance = 0.3
    
    for iteration in range(max_iterations):
        # Predict current difficulty
        predicted_stars = star_predictor.predict(beatmap)
        
        if abs(predicted_stars - target_stars) < tolerance:
            break
        
        # Adjust parameters
        if predicted_stars > target_stars:
            # Reduce difficulty
            decrease_difficulty(beatmap)
        else:
            # Increase difficulty
            increase_difficulty(beatmap)
    
    return beatmap
```

## Continuous Learning

### User Feedback Collection

```python
def collect_user_feedback(beatmap_id: str, rating: int, comments: str = None):
    """
    Collect user ratings and feedback on generated beatmaps.
    
    Args:
        beatmap_id: Generated beatmap ID
        rating: 1-5 stars
        comments: Optional user comments
    """
    store_feedback({
        'beatmap_id': beatmap_id,
        'rating': rating,
        'comments': comments,
        'timestamp': datetime.now()
    })
    
    # Trigger retraining if threshold of feedback is reached
    if feedback_count() > 1000:
        schedule_model_retraining()
```

### Model Retraining

```python
def retrain_models():
    """
    Periodically retrain models with new feedback data.
    """
    print("Starting model retraining...")
    
    # Collect new training data
    new_data = collect_recent_feedback()
    
    # Train each model
    train_pattern_predictor()
    train_star_predictor()
    train_style_classifier()
    
    # Validate on test set
    if validate_models():
        # Deploy new models
        deploy_models()
        print("Models updated successfully")
    else:
        print("Validation failed, keeping old models")
```

## Performance Optimization

### Model Quantization

```python
def quantize_model(model_path: str) -> str:
    """
    Convert TensorFlow model to quantized ONNX for faster inference.
    """
    # Load TensorFlow model
    model = keras.models.load_model(model_path)
    
    # Convert to ONNX
    import onnx
    import keras2onnx
    
    onnx_model = keras2onnx.convert_keras(model)
    onnx_path = model_path.replace('.h5', '.onnx')
    onnx.save_model(onnx_model, onnx_path)
    
    # Quantize (dynamic quantization)
    from onnxruntime.quantization import quantize_dynamic
    
    quantized_path = model_path.replace('.onnx', '_quant.onnx')
    quantize_dynamic(onnx_path, quantized_path)
    
    return quantized_path
```

### Batch Prediction

```python
def predict_patterns_batch(audio_features: np.ndarray) -> np.ndarray:
    """
    Predict patterns for entire beatmap at once.
    """
    # Shape: (n_beats, n_features) -> (n_beats, n_patterns)
    predictions = pattern_predictor.predict(audio_features, batch_size=256)
    return predictions
```

## Monitoring

### Model Performance Metrics

```python
def log_model_metrics():
    """
    Log current model performance for monitoring.
    """
    metrics = {
        'pattern_accuracy': evaluate_on_test_set('pattern_predictor'),
        'star_rating_mae': evaluate_on_test_set('star_predictor'),
        'style_accuracy': evaluate_on_test_set('style_classifier'),
        'inference_time_ms': measure_inference_time(),
        'model_size_mb': get_model_size(),
        'user_satisfaction': get_average_user_rating(),
    }
    
    log_to_prometheus(metrics)
```

## Timeline

- **Week 1-2**: Data collection and preparation
- **Week 3-4**: Model training and validation
- **Week 5-6**: Integration with mapping engine
- **Week 7-8**: Testing and optimization
- **Week 9-10**: Deployment and monitoring

---

**This architecture is designed to evolve with user feedback and real-world performance data.**
