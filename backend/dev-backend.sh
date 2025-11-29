#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Start Postgres container
echo "Starting dev DB container (bookitgy-dev-db)..."
sudo docker start bookitgy-dev-db || echo "DB container already running or not found."

# Activate venv
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Show DATABASE_URL
echo "DATABASE_URL is: $DATABASE_URL"

# Start uvicorn
echo "Starting FastAPI on http://0.0.0.0:8002 ..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
