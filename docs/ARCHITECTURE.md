# BeatForge Architecture Documentation

## System Overview

BeatForge is a production-grade web application that automatically generates playable osu!standard beatmaps from MP3 files. The system combines advanced audio analysis with a sophisticated mapping engine that simulates real mapper behavior.

## Architecture Principles

1. **Modularity**: Each component (audio analysis, pattern generation, osu file writing) is independent and testable
2. **Scalability**: Asynchronous processing with Celery and Redis for handling multiple concurrent users
3. **Maintainability**: Clear separation of concerns, comprehensive logging, and extensive documentation
4. **Quality**: Production-grade error handling, validation, and type safety throughout
5. **Future-Ready**: ML integration points for training custom models and improving generation quality

## Technology Stack

### Frontend
- **Next.js 14+**: React framework with file routing and API routes
- **React 18+**: UI component library
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Server state management
- **Axios**: HTTP client

### Backend
- **Python 3.11+**: Core language
- **FastAPI**: High-performance async web framework
- **Pydantic V2**: Data validation and serialization
- **SQLAlchemy**: ORM for database operations
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching

### Audio Processing
- **librosa**: Music and audio analysis
- **numpy/scipy**: Numerical computing
- **soundfile**: Audio I/O
- **essentia**: Advanced audio features (optional)

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **PostgreSQL**: Persistent data storage
- **Nginx**: Reverse proxy

## Directory Structure

```
BeatForge/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app factory
│   │   ├── config.py                  # Configuration management
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── upload.py      # File upload endpoints
│   │   │   │   │   ├── generate.py    # Generation endpoints
│   │   │   │   │   ├── jobs.py        # Job status endpoints
│   │   │   │   │   └── download.py    # Download endpoints
│   │   │   │   └── router.py          # API router assembly
│   │   ├── audio/
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py            # Main audio analysis orchestrator
│   │   │   ├── bpm_detector.py        # BPM detection
│   │   │   ├── beat_detector.py       # Beat detection
│   │   │   ├── onset_detector.py      # Onset detection
│   │   │   ├── energy_detector.py     # RMS energy analysis
│   │   │   ├── spectral_features.py   # Spectral analysis
│   │   │   ├── section_detector.py    # Musical section identification
│   │   │   ├── silence_detector.py    # Silence detection
│   │   │   └── musical_features/
│   │   │       ├── __init__.py
│   │   │       ├── kick_snare_detector.py
│   │   │       ├── vocal_detector.py
│   │   │       └── drop_detector.py
│   │   ├── mapping/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py              # Main mapping engine orchestrator
│   │   │   ├── cursor_momentum.py     # Cursor state & movement
│   │   │   ├── pattern_generator.py   # Pattern generation logic
│   │   │   ├── difficulty_manager.py  # Difficulty-based parameters
│   │   │   ├── pattern_memory.py      # Pattern history & avoiding repetition
│   │   │   ├── musical_mapper.py      # Audio event → pattern mapping
│   │   │   ├── advanced_streams/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stream_generator.py
│   │   │   │   ├── burst_generator.py
│   │   │   │   └── jump_stream_generator.py
│   │   │   └── sliders/
│   │   │       ├── __init__.py
│   │   │       ├── slider_generator.py
│   │   │       ├── bezier_curves.py
│   │   │       └── slider_validator.py
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── pattern_predictor.py   # ML-based pattern prediction
│   │   │   ├── star_rating_predictor.py # Difficulty prediction
│   │   │   └── style_classifier.py    # Mapping style classification
│   │   ├── osu/
│   │   │   ├── __init__.py
│   │   │   ├── osu_file_writer.py     # .osu file generation
│   │   │   ├── osz_packager.py        # .osz archive creation
│   │   │   ├── models.py              # OSU file data models
│   │   │   └── validators.py          # OSU format validation
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── generation_service.py  # Orchestrates full generation
│   │   │   ├── storage_service.py     # File storage management
│   │   │   ├── database_service.py    # DB operations
│   │   │   └── cache_service.py       # Redis caching
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # SQLAlchemy models
│   │   │   ├── schemas.py             # Pydantic schemas
│   │   │   └── enums.py               # Enumerations
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   └── celery_tasks.py        # Celery task definitions
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py             # Logging configuration
│   │   │   ├── exceptions.py          # Custom exceptions
│   │   │   ├── validators.py          # Input validation utilities
│   │   │   └── converters.py          # Data conversion utilities
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── error_handler.py       # Global error handling
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest configuration
│   │   ├── test_audio_analyzer.py     # Audio analysis tests
│   │   ├── test_mapping_engine.py     # Mapping engine tests
│   │   ├── test_osu_writer.py         # OSU file generation tests
│   │   └── test_api.py                # API endpoint tests
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment variables template
│   └── celery_config.py               # Celery configuration
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx             # Root layout
│   │   │   ├── page.tsx               # Home page
│   │   │   ├── generation/
│   │   │   │   └── [jobId]/
│   │   │   │       └── page.tsx       # Generation progress page
│   │   │   ├── results/
│   │   │   │   └── [jobId]/
│   │   │   │       └── page.tsx       # Results page
│   │   │   └── api/
│   │   │       └── proxy/
│   │   │           └── [...path].ts   # Backend proxy
│   │   ├── components/
│   │   │   ├── UploadArea.tsx         # Upload component
│   │   │   ├── SettingsForm.tsx       # Settings form
│   │   │   ├── ProgressIndicator.tsx  # Progress display
│   │   │   └── ResultsDisplay.tsx     # Results display
│   │   ├── hooks/
│   │   │   ├── useGeneration.ts       # Generation logic hook
│   │   │   └── useJobStatus.ts        # Job status polling hook
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client
│   │   │   └── types.ts               # TypeScript types
│   │   └── styles/
│   │       └── globals.css            # Global styles
│   ├── public/
│   ├── .env.local.example             # Frontend env template
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.ts             # TailwindCSS configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   └── package.json                   # Node.js dependencies
├── docker/
│   ├── Dockerfile.backend             # Backend container
│   ├── Dockerfile.frontend            # Frontend container
│   └── nginx.conf                     # Nginx configuration
├── docker-compose.yml                 # Multi-container orchestration
├── docs/
│   ├── ARCHITECTURE.md                # This file
│   ├── BACKEND_DEV.md                 # Backend development guide
│   ├── FRONTEND_DEV.md                # Frontend development guide
│   ├── ML_ARCHITECTURE.md             # ML system design
│   ├── DEPLOYMENT.md                  # Deployment guide
│   ├── API.md                         # API documentation
│   └── DATABASE.md                    # Database schema
├── ROADMAP.md                         # Development roadmap
└── README.md                          # Project overview
```

## Data Flow

### Generation Pipeline

```
1. User Upload
   └─ File validation
      └─ Storage in temporary location
         └─ Job creation (DB)
            └─ Celery task enqueue

2. Audio Analysis (Worker)
   └─ Load MP3 file
      └─ Compute STFT/Spectrogram
         └─ BPM detection
            └─ Beat detection
               └─ Onset detection
                  └─ Energy extraction
                     └─ Section detection
                        └─ Musical feature detection
                           └─ Store analysis results (Cache + DB)

3. Mapping Generation (Worker)
   └─ Load audio analysis results
      └─ Initialize cursor state
         └─ For each beat/timestamp:
            ├─ Detect audio events (kicks, snares, vocals)
            ├─ Query pattern predictor (if ML enabled)
            ├─ Generate pattern based on difficulty/style
            ├─ Update cursor momentum
            └─ Store hit object
         └─ Smooth cursor transitions
            └─ Validate beatmap

4. OSU File Generation
   └─ Create timing points from BPM data
      └─ Create hit objects from pattern
         └─ Apply difficulty settings
            └─ Write .osu file
               └─ Package .osz (MP3 + .osu + metadata)
                  └─ Upload to storage
                     └─ Update job status
                        └─ Notify user
```

## API Endpoints

### Authentication & Status
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - System status

### Upload & Generation
- `POST /api/v1/upload` - Upload MP3 file
- `POST /api/v1/generate` - Start generation job
- `GET /api/v1/jobs/{job_id}` - Get job status
- `GET /api/v1/jobs/{job_id}/download` - Download .osz file
- `GET /api/v1/jobs/{job_id}/preview` - Get .osu file preview
- `DELETE /api/v1/jobs/{job_id}` - Cancel/delete job

### Analytics (Future)
- `GET /api/v1/analytics/stats` - System statistics
- `POST /api/v1/feedback` - User feedback

## Database Schema

### Tables
- `songs` - Uploaded MP3 metadata
- `jobs` - Generation jobs and status
- `beatmaps` - Generated beatmap records
- `job_logs` - Detailed job logs for debugging
- `user_sessions` - User tracking (optional)

## Performance Considerations

1. **Asynchronous Processing**: All heavy computation (audio analysis, mapping generation) runs in Celery workers, keeping the API responsive
2. **Caching**: Audio analysis results cached in Redis to avoid re-analysis
3. **File Storage**: Temporary files cleaned up after successful packaging
4. **Database Indexing**: Job status queries optimized with proper indices
5. **Horizontal Scaling**: Additional workers can be added for increased throughput

## Error Handling

1. **Validation**: Input validation at API and service layers
2. **Recovery**: Celery retry logic for transient failures
3. **Logging**: Comprehensive logging at each stage for debugging
4. **User Feedback**: Clear error messages returned to frontend
5. **Monitoring**: Prometheus metrics for system health

## Future ML Integration

### Phase 1: Pattern Prediction
- Train on existing osu! beatmaps
- Predict likely pattern types for audio contexts
- Integrate into mapping engine for improved generation

### Phase 2: Star Rating Prediction
- Predict difficulty based on generated beatmap
- Adjust generation parameters to hit target difficulty

### Phase 3: Style Imitation
- Classify mapper styles from existing beatmaps
- Allow users to select mapping style
- Generate beatmaps in selected style

### Phase 4: Continuous Improvement
- Collect user feedback on generated beatmaps
- Retrain models on feedback data
- Iterative improvement cycle
