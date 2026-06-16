# BeatForge - Backend Development

## Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- pip / venv

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your settings
```

### Database Initialization

```bash
python app/db_init.py
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Celery Worker

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

### Running Tests

```bash
pytest
pytest -v  # Verbose
pytest --cov=app  # With coverage
```

## Architecture

```
app/
├── api/              # API endpoints
│   └── v1/
│       └── endpoints/
├── audio/            # Audio analysis
│   ├── analyzer.py
│   └── processors.py
├── mapping/          # Beatmap generation
│   ├── engine.py
│   ├── cursor_physics.py
│   ├── pattern_grammar.py
│   └── difficulty_calculator.py
├── osu/              # OSU file format
│   └── writer.py
├── services/         # Business logic
├── models/           # Database models
├── workers/          # Celery tasks
└── utils/            # Utilities
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Key Concepts

### Cursor Physics
The `CursorPhysics` class simulates real osu! cursor behavior:
- Velocity and momentum
- Friction and acceleration
- Direction smoothing
- Playfield constraints

### Pattern Grammar
The `PatternGrammar` generates human-like patterns:
- Streams (alternating circles)
- Bursts (rapid clusters)
- Jumps (large distances)
- Wiggles, triangles, arcs
- Pattern memory (prevents repetition)

### Audio Analysis
Comprehensive audio feature extraction:
- BPM and beat tracking
- Onset detection
- Energy envelope
- Section detection (intro, verse, drop, etc.)
- Spectral analysis

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests: `pytest`
4. Commit: `git commit -m "Add feature description"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

## Debugging

Enable debug logging:

```python
from loguru import logger
logger.enable("app")
```

## Performance Tips

- Use Redis caching for frequent queries
- Process audio files asynchronously via Celery
- Implement database indexing on frequently queried columns
- Cache analysis results

## Common Issues

### Audio file not loading
- Ensure librosa and soundfile are installed
- Check file format (MP3 supported)
- Verify file exists and is readable

### Database connection errors
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Run migrations: `python app/db_init.py`

### Celery tasks not executing
- Ensure Redis is running
- Check Celery worker is started
- Verify CELERY_BROKER_URL in .env
