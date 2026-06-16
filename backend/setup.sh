#!/bin/bash
cd "$(dirname "$0")"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  cat > .env << EOF
# Database
DATABASE_URL=postgresql://beatforge:beatforge@postgres:5432/beatforge

# Redis
REDIS_URL=redis://redis:6379

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# App
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
EOF
  echo "Created .env file"
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Initialize database
echo "Initializing database..."
python backend/app/db_init.py

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Setup complete!"
