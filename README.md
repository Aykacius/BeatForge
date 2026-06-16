# BeatForge - Automatic osu!standard Beatmap Generation

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://www.typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Overview

BeatForge is a production-grade web application that automatically generates playable osu!standard beatmaps from MP3 files. The system combines advanced audio analysis with a sophisticated mapping engine that simulates real mapper behavior.

## Features

- 🎵 **Advanced Audio Analysis**
  - BPM detection
  - Beat grid generation
  - Onset detection
  - Energy analysis
  - Spectral feature extraction
  - Musical section identification
  - Silence detection

- 🎮 **Intelligent Mapping Engine**
  - Cursor momentum system for flow preservation
  - Pattern grammar (streams, jumps, sliders, bursts)
  - Difficulty-based parameter adjustment
  - Pattern memory to avoid repetition
  - Musical event mapping (kicks, snares, vocals)

- 🎯 **User-Friendly Interface**
  - Drag-and-drop MP3 upload
  - Difficulty selection (Easy → Expert+)
  - Mapping style options (Technical, Jump, Hybrid, Aim, Stream Practice)
  - Target star rating (2★ - 9★)
  - Real-time progress tracking
  - Instant download of generated beatmaps

- ⚡ **Production-Ready Architecture**
  - Asynchronous processing with Celery
  - Redis caching
  - PostgreSQL persistence
  - Docker containerization
  - Comprehensive logging and monitoring
  - Error handling and recovery

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OR Python 3.11+, Node.js 18+, PostgreSQL 14+, Redis 7+

### Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/Aykacius/BeatForge.git
cd BeatForge

# Start all services
docker-compose up -d

# Wait for services to be ready (~30 seconds)
sleep 30

# Run migrations
docker-compose exec backend python -m alembic upgrade head

# Open browser
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Local Development

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start FastAPI server
uvicorn app.main:app --reload

# In another terminal, start Celery worker
celery -A app.workers.celery_tasks worker --loglevel=info
```

#### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev

# Open http://localhost:3000
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│                   (Next.js Frontend)                    │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    ┌─────▼────┐   ┌────▼─────┐  ┌───▼──────┐
    │  Nginx   │   │ FastAPI  │  │  Redis   │
    │ (Reverse │   │   API    │  │  Cache   │
    │  Proxy)  │   │          │  │          │
    └──────────┘   └────┬─────┘  └──────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌─────▼──────┐  ┌───▼──────┐  ┌──▼──────┐
    │  Celery    │  │PostgreSQL│  │ Storage │
    │  Workers   │  │   DB     │  │ (Files) │
    │            │  │          │  │         │
    │ • Audio    │  └──────────┘  └─────────┘
    │   Analysis │
    │ • Mapping  │
    │   Engine   │
    └────────────┘
```

## Project Structure

```
BeatForge/
├── backend/                    # Python FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/  # REST endpoints
│   │   ├── audio/             # Audio analysis modules
│   │   ├── mapping/           # Mapping engine
│   │   ├── ml/                # ML models (future)
│   │   ├── osu/               # OSU file handling
│   │   ├── services/          # Business logic
│   │   ├── models/            # Data models
│   │   ├── workers/           # Celery tasks
│   │   └── utils/             # Utilities
│   ├── tests/                 # Unit and integration tests
│   ├── requirements.txt        # Python dependencies
│   └── celery_config.py        # Celery configuration
│
├── frontend/                   # Next.js React application
│   ├── src/
│   │   ├── app/              # Pages and layouts
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Utilities and API client
│   │   └── styles/           # Global styles
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── tailwind.config.ts    # TailwindCSS config
│
├── docker/                    # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── BACKEND_DEV.md
│   ├── FRONTEND_DEV.md
│   ├── ML_ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── API.md
│   └── DATABASE.md
│
├── docker-compose.yml         # Multi-container orchestration
├── ROADMAP.md                # Development roadmap
└── README.md                 # This file
```

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Python 3.11+** - Core language
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Celery** - Async task queue
- **Redis** - Message broker & cache
- **librosa** - Audio analysis
- **numpy/scipy** - Numerical computing

### Frontend
- **Next.js 14+** - React framework
- **React 18+** - UI library
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **React Query** - State management

### Infrastructure
- **PostgreSQL** - Database
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Redis** - Cache/broker

## API Documentation

### Endpoints

- `POST /api/v1/upload` - Upload MP3 file
- `POST /api/v1/generate` - Start beatmap generation
- `GET /api/v1/jobs/{job_id}` - Get job status
- `GET /api/v1/jobs/{job_id}/download` - Download generated beatmap
- `GET /api/v1/health` - Health check

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Code Structure

```python
# Audio Analysis Pipeline
AudioAnalyzer
├── detect_bpm()
├── detect_beats()
├── detect_onsets()
├── extract_energy()
├── extract_spectral_features()
├── detect_sections()
└── detect_silence()

# Mapping Engine
MappingEngine
├── CursorMomentum (flow preservation)
├── PatternGenerator (circle/stream/slider generation)
├── DifficultyManager (parameter mapping)
├── PatternMemory (avoid repetition)
└── MusicalMapper (event → pattern mapping)

# OSU File Writer
OSUFileWriter
├── create_timing_points()
├── create_hit_objects()
├── create_metadata()
├── validate_format()
└── write_file()
```

### Running Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=app tests/        # With coverage
pytest -k "test_bpm"           # Specific tests
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/beatforge

# Redis
REDIS_URL=redis://localhost:6379/0

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Storage
STORAGE_PATH=/tmp/beatforge
MAX_FILE_SIZE=52428800  # 50MB

# Logging
LOG_LEVEL=INFO
```

## Performance

- **Audio Analysis**: ~5-30 seconds (depends on MP3 length)
- **Beatmap Generation**: ~10-60 seconds (depends on difficulty)
- **Packaging**: ~2-5 seconds
- **Concurrent Users**: Scales horizontally with Celery workers

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/api/v1/health
```

### Celery Monitoring

```bash
celery -A app.workers.celery_tasks flower
# Open http://localhost:5555
```

### Database Monitoring

```sql
SELECT status, COUNT(*) as count FROM jobs GROUP BY status;
```

## Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- AWS deployment
- Load balancing
- SSL/TLS
- Monitoring and alerting
- Backup strategies

## Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make changes following code style
3. Write/update tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

## Roadmap

### Phase 1: Core Generation ✅
- Audio analysis
- Basic mapping engine
- OSU file generation
- Web interface

### Phase 2: Advanced Features
- ML-based pattern prediction
- Star rating prediction
- Mapper style classification
- Batch processing

### Phase 3: Optimization
- Performance optimization
- Result caching
- Progressive loading
- Advanced analytics

### Phase 4: Community
- User feedback system
- Leaderboards
- Community maps
- Style marketplace

See [ROADMAP.md](ROADMAP.md) for detailed timeline.

## Troubleshooting

### Common Issues

**Celery tasks not processing**
```bash
# Check if worker is running
celery -A app.workers.celery_tasks inspect active

# Check Redis connection
redis-cli ping  # Should return PONG
```

**Database connection errors**
```bash
# Verify PostgreSQL is running
psql $DATABASE_URL

# Run migrations
alembic upgrade head
```

**Audio analysis timeout**
- Increase Celery task timeout in `celery_config.py`
- Use larger workers for CPU-intensive tasks

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions:
1. Check existing [Issues](https://github.com/Aykacius/BeatForge/issues)
2. Create a new issue with detailed description
3. Submit Pull Requests for contributions

## Acknowledgments

- osu! community for inspiration
- librosa for audio analysis
- FastAPI for amazing framework
- Next.js for frontend framework

---

**Made with ❤️ for the osu! community**
