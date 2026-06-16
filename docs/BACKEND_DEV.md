# Backend Development Guide

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/Aykacius/BeatForge.git
cd BeatForge/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Configure .env with your settings
# Update DATABASE_URL, REDIS_URL, etc.

# Run migrations (if applicable)
# alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.workers.celery_tasks worker --loglevel=info

# Optional: Start Celery beat (for scheduled tasks)
celery -A app.workers.celery_tasks beat --loglevel=info
```

### Using Docker Compose

```bash
cd BeatForge
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run migrations
docker-compose exec backend alembic upgrade head
```

## Project Structure Explanation

### `app/main.py`
FastAPI application factory. Sets up middleware, error handlers, and routers.

### `app/config.py`
Configuration management using Pydantic Settings. Loads from environment variables.

### `app/api/v1/endpoints/`
REST API endpoints organized by feature.

### `app/audio/`
Audio analysis modules:
- **analyzer.py**: Orchestrates all audio analysis tasks
- **bpm_detector.py**: Detects tempo using onset-based method
- **beat_detector.py**: Identifies beat grid from BPM
- **onset_detector.py**: Detects audio transients
- **energy_detector.py**: Extracts RMS energy curves
- **spectral_features.py**: Computes MFCCs, spectral centroids, etc.
- **section_detector.py**: Identifies musical sections
- **silence_detector.py**: Detects silent portions

### `app/mapping/`
Mapping engine modules:
- **engine.py**: Main orchestrator that controls generation flow
- **cursor_momentum.py**: Tracks cursor state (position, velocity, direction)
- **pattern_generator.py**: Generates individual patterns
- **difficulty_manager.py**: Maps difficulty to spacing/density parameters
- **pattern_memory.py**: Tracks recent patterns to avoid repetition
- **musical_mapper.py**: Maps audio events to pattern types

### `app/osu/`
OSU file format handling:
- **osu_file_writer.py**: Generates valid .osu files
- **osz_packager.py**: Creates .osz archives
- **models.py**: Data models for OSU components
- **validators.py**: Validates OSU format compliance

### `app/services/`
Business logic services:
- **generation_service.py**: Orchestrates the complete generation pipeline
- **storage_service.py**: Handles file I/O (uploads, downloads, cleanup)
- **database_service.py**: Database operations
- **cache_service.py**: Redis operations

### `app/models/`
Data models:
- **database.py**: SQLAlchemy ORM models
- **schemas.py**: Pydantic validation schemas
- **enums.py**: Enumeration types

### `app/workers/`
Celery task definitions for asynchronous processing.

## Core Modules Deep Dive

### Audio Analysis Pipeline

#### BPM Detection (`bpm_detector.py`)

Implements onset-based BPM detection:
```python
1. Compute onset strength (audio transients)
2. Auto-correlate onset strength
3. Find peaks in autocorrelation (tempo candidates)
4. Validate with spectral features
5. Return most likely BPM
```

#### Beat Detection (`beat_detector.py`)

Given BPM, creates beat grid:
```python
1. Use librosa.beat.beat_track() for beat positions
2. Adjust beat positions to align with onsets
3. Interpolate for smooth beat grid
4. Return beat times in seconds
```

#### Section Detection (`section_detector.py`)

Identifies musical sections (intro, verse, drop, etc.):
```python
1. Compute MFCCs (timbral features)
2. Compute novelty curve from MFCC changes
3. Find peaks in novelty curve (section boundaries)
4. Classify sections based on energy and features
5. Return section timeline
```

### Mapping Engine

#### Cursor Momentum (`cursor_momentum.py`)

Tracks cursor state to ensure smooth flow:
```python
class CursorState:
    position: (x, y)          # Current screen position
    velocity: magnitude       # Movement speed
    direction: angle          # Direction of movement
    angle_memory: float       # Weighted history of angles
    last_update_time: float   # When cursor was last updated
```

Movement calculation:
```python
new_position = calculate_flow_friendly_position(
    current_position=cursor.position,
    target_time=beat_time,
    allowed_distance=difficulty.spacing,
    angle_preference=cursor.direction
)
```

#### Pattern Generation (`pattern_generator.py`)

Generates patterns based on audio context:
```python
Pattern types:
- Circle: Single tap
- Stream: Fast sequence of circles
- Burst: Medium-speed circles
- Jump: Large spacing between objects
- Slider: Curved path to follow
- Wiggle: Rapid back-and-forth

Generation considers:
- Audio event type (kick, snare, vocal)
- Difficulty level
- Recent pattern history
- Cursor momentum
- Section type (build-up vs. drop)
```

#### Difficulty System (`difficulty_manager.py`)

Maps difficulty setting to parameters:
```python
Difficulty.EASY:
  spacing: 100-150px
  object_density: 2-3 per second
  max_stream_length: 3
  jump_distance: 50-100px

Difficulty.NORMAL:
  spacing: 150-200px
  object_density: 3-4 per second
  max_stream_length: 5
  jump_distance: 100-150px

...(and so on)
```

## API Implementation

### Upload Endpoint

```python
POST /api/v1/upload
Content-Type: multipart/form-data

Request:
  file: <MP3 file>

Response (201):
  {
    "song_id": "uuid",
    "filename": "song.mp3",
    "duration": 180.5,
    "file_size": 5242880
  }
```

### Generation Endpoint

```python
POST /api/v1/generate
Content-Type: application/json

Request:
  {
    "song_id": "uuid",
    "difficulty": "HARD",
    "mapping_style": "TECHNICAL_STREAM",
    "target_star_rating": 5.5
  }

Response (202):
  {
    "job_id": "uuid",
    "status": "QUEUED",
    "created_at": "2024-01-01T12:00:00Z"
  }
```

### Job Status Endpoint

```python
GET /api/v1/jobs/{job_id}

Response (200):
  {
    "job_id": "uuid",
    "status": "GENERATING",
    "progress": 45,
    "current_stage": "Generating patterns...",
    "estimated_time_remaining": 30,
    "result": null
  }
```

## Database Schema

### Songs Table
```sql
CREATE TABLE songs (
  id UUID PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255),
  duration FLOAT NOT NULL,
  file_size BIGINT NOT NULL,
  file_path VARCHAR(512),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  song_id UUID NOT NULL REFERENCES songs(id),
  status VARCHAR(50) NOT NULL,
  difficulty VARCHAR(50) NOT NULL,
  mapping_style VARCHAR(50) NOT NULL,
  target_star_rating FLOAT,
  progress INTEGER DEFAULT 0,
  current_stage VARCHAR(255),
  result JSON,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX (status),
  INDEX (created_at)
);
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_audio_analyzer.py

# Run tests matching pattern
pytest -k "test_bpm_detection"
```

### Test Structure

```python
# tests/test_audio_analyzer.py

import pytest
from app.audio.analyzer import AudioAnalyzer
from pathlib import Path

@pytest.fixture
def sample_mp3():
    """Provide path to test MP3 file"""
    return Path('tests/fixtures/sample_120bpm.mp3')

def test_bpm_detection(sample_mp3):
    analyzer = AudioAnalyzer()
    bpm = analyzer.detect_bpm(str(sample_mp3))
    assert 115 <= bpm <= 125  # Allow 5 BPM tolerance

def test_beat_detection(sample_mp3):
    analyzer = AudioAnalyzer()
    beats = analyzer.detect_beats(str(sample_mp3), bpm=120)
    assert len(beats) > 0
    assert all(beats[i] < beats[i+1] for i in range(len(beats)-1))
```

## Debugging

### Enable Debug Logging

In `.env`:
```
LOG_LEVEL=DEBUG
```

### View Celery Task Logs

```bash
# In production, use Flower for Celery monitoring
pip install flower
celery -A app.workers.celery_tasks flower
# Open http://localhost:5555
```

### Database Debugging

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# View recent jobs
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 10;

# Check job status
SELECT status, COUNT(*) FROM jobs GROUP BY status;
```

## Performance Optimization

1. **Audio Analysis Caching**: Cache librosa spectrograms in Redis
2. **Beat Detection**: Use vectorized numpy operations
3. **Pattern Generation**: Use numpy for coordinate calculations
4. **Database Queries**: Use proper indexing and pagination
5. **Celery**: Use task routing to separate CPU-bound and I/O-bound tasks

## Deployment Checklist

- [ ] Set all required environment variables
- [ ] Configure database with proper backups
- [ ] Set up Redis for caching and Celery
- [ ] Configure file storage (local or S3)
- [ ] Set up logging and monitoring
- [ ] Configure CORS for frontend domain
- [ ] Run database migrations
- [ ] Test all endpoints
- [ ] Set up health checks
- [ ] Configure rate limiting
