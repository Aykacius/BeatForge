# BeatForge - Architecture Documentation

## System Overview

```
┌─────────────────┐
│   Next.js UI    │
│  (React 18)     │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────┐
│   FastAPI Backend               │
│  (Python 3.11)                  │
│  ├─ Upload Endpoint             │
│  ├─ Generation Endpoint         │
│  ├─ Job Status Tracking         │
│  └─ Download Endpoint           │
└────────┬──────────────┬──────────┘
         │              │
    ┌────▼────┐    ┌────▼─────┐
    │ Celery   │    │ Database  │
    │ Worker   │    │(PostgreSQL)│
    └────┬────┘    └───────────┘
         │
    ┌────▼──────────────┐
    │  Audio Processing │
    │  & Mapping Engine │
    │  ├─ librosa       │
    │  ├─ numpy/scipy   │
    │  └─ Algorithms    │
    └──────────────────┘
         │
    ┌────▼──────────┐
    │ .osu File     │
    │ Generator     │
    └───────────────┘
         │
    ┌────▼──────────┐
    │ Cache/Storage │
    │ (Redis)       │
    └───────────────┘
```

## Core Components

### 1. Audio Analysis Pipeline

**Location**: `backend/app/audio/`

**Responsibilities**:
- Load and decode MP3 files
- Extract audio features (BPM, beats, onsets)
- Detect song structure (intro, verse, drop, etc.)
- Analyze energy envelope
- Compute spectral features

**Key Modules**:
- `AudioAnalyzer`: Main orchestrator
- `BPMDetector`: Tempo estimation
- `BeatDetector`: Beat tracking
- `OnsetDetector`: Attack point detection
- `SectionDetector`: Song segmentation
- `EnergyAnalyzer`: RMS energy tracking

### 2. Mapping Engine

**Location**: `backend/app/mapping/`

**Responsibilities**:
- Generate hit object sequences
- Apply cursor physics
- Create human-like patterns
- Adapt to audio features
- Calculate difficulty metrics

**Key Modules**:
- `MappingEngine`: Main generator
- `CursorPhysics`: Movement simulation
- `PatternGrammar`: Pattern generation
- `DifficultyCalculator`: Metrics computation

### 3. OSU File Writer

**Location**: `backend/app/osu/`

**Responsibilities**:
- Generate valid .osu files
- Format hit objects correctly
- Create .osz archives
- Embed metadata

### 4. API Layer

**Location**: `backend/app/api/`

**Endpoints**:
- `POST /api/v1/upload/` - Upload MP3
- `POST /api/v1/generate/` - Start generation
- `GET /api/v1/jobs/{job_id}` - Job status
- `GET /api/v1/download/{job_id}` - Download beatmap

### 5. Frontend UI

**Location**: `frontend/src/`

**Pages**:
- `/` - Home
- `/upload` - Upload & generation interface

**Components**:
- `FileUpload`: File drag-and-drop
- `GenerationSettings`: Configuration
- `ProgressDisplay`: Real-time status

## Data Flow

### Generation Workflow

```
User Upload
    ↓
[Upload Endpoint]
    ├─ Validate MP3
    ├─ Save to storage
    └─ Return file_id
    ↓
[Generation Request]
    ├─ Create Celery task
    ├─ Return job_id
    └─ Queue for processing
    ↓
[Audio Analysis] (Async)
    ├─ Load MP3
    ├─ Compute BPM/beats
    ├─ Detect sections
    └─ Extract features
    ↓
[Mapping Engine] (Async)
    ├─ Generate patterns
    ├─ Apply physics
    └─ Create hit objects
    ↓
[OSU Writer] (Async)
    ├─ Format .osu file
    ├─ Package .osz
    └─ Save to storage
    ↓
[Status Check] (User Polling)
    ├─ Get job_id
    ├─ Query progress
    └─ Display UI updates
    ↓
[Download]
    ├─ Fetch .osz
    └─ User plays in osu!
```

## Database Schema

### songs
```sql
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(36) UNIQUE,
    filename VARCHAR(255),
    file_path VARCHAR(500),
    size_bytes INT,
    duration FLOAT,
    bpm FLOAT,
    created_at TIMESTAMP
);
```

### generation_jobs
```sql
CREATE TABLE generation_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(36) UNIQUE,
    song_id INT REFERENCES songs(id),
    difficulty VARCHAR(20),
    mapping_style VARCHAR(50),
    target_star_rating FLOAT,
    status VARCHAR(20),  -- queued, processing, completed, failed
    progress INT,
    output_path VARCHAR(500),
    error_message TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### generated_beatmaps
```sql
CREATE TABLE generated_beatmaps (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(36) REFERENCES generation_jobs(job_id),
    osu_file_path VARCHAR(500),
    star_rating FLOAT,
    object_count INT,
    metadata JSON,
    created_at TIMESTAMP
);
```

## Cursor Physics Algorithm

### Key Features

1. **Momentum Preservation**
   - Cursor velocity carries over between objects
   - Friction gradually decays velocity
   - Max velocity cap prevents unrealistic speeds

2. **Direction Smoothing**
   - Can't turn instantly (max turn rate)
   - Smooth curves instead of sharp angles
   - Angle memory for pattern flow

3. **Playfield Constraints**
   - Keep cursor within 512x384 playfield
   - Bounce or clamp at boundaries

### Physics Parameters

```python
friction = 0.95  # Velocity decay per frame
max_velocity = 500.0  # pixels/second
max_turn_rate = 0.3  # radians/update
```

## Pattern Grammar System

### Pattern Types

1. **Stream**: Rapid alternating circles
   ```
   X . X . X . X . X
   ```

2. **Burst**: 3-4 rapid circles in cluster
   ```
      X
   X    X
     X
   ```

3. **Jump**: Two distant circles
   ```
   X                    X
   ```

4. **Wiggle**: Curved alternating path
   ```
    X
   X X
    X
     X
   ```

5. **Triangle/Square**: Geometric shapes

### Pattern Selection

Based on:
- Audio section (intro, drop, etc.)
- Energy level
- Mapping style preference
- Difficulty level
- Pattern history (avoid repetition)

## Difficulty Calculation

### Star Rating Formula

```
SR = sqrt(aim_difficulty² + speed_difficulty²) / 10
```

Where:
- **Aim Difficulty**: Based on spacing and angles
- **Speed Difficulty**: Based on timing and BPM

### Difficulty Settings by Level

| Level | HP | CS | OD | AR | Spacing |
|-------|----|----|----|----|----------|
| Easy | 4.0 | 4.0 | 4.0 | 4.0 | 80-150 |
| Normal | 5.0 | 4.0 | 5.0 | 5.0 | 100-180 |
| Hard | 6.0 | 3.8 | 6.0 | 6.5 | 120-220 |
| Insane | 7.0 | 3.5 | 8.0 | 8.0 | 140-280 |
| Expert+ | 8.0 | 3.0 | 9.0 | 9.5 | 150-300 |

## Performance Considerations

### Audio Processing
- Librosa lazy-loads chunks (memory efficient)
- FFT computed once and cached
- Parallel processing for independent features

### Mapping Generation
- Physics calculations O(n) where n = object count
- Pattern memory prevents O(n²) repetition checks
- Pre-computed difficulty lookups

### Database
- Indexes on `job_id`, `file_id`, `song_id`
- Connection pooling
- Async queries via SQLAlchemy

## Future Architecture Enhancements

### Phase 2: Machine Learning
- Pattern prediction model
- Mapper style imitation
- Star rating estimation
- Human feedback training loop

### Phase 3: Distributed Processing
- Horizontal scaling of Celery workers
- GPU acceleration for audio processing
- Cloud storage integration (S3, GCS)

### Phase 4: Real-time Collaboration
- WebSocket for live preview
- Multi-user editing
- Version control for beatmaps
