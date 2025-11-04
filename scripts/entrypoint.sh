#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
sleep 2

echo "Checking if Aerich is initialized..."
if [ ! -d "migrations" ]; then
    echo "Initializing Aerich for the first time..."
    python -m aerich init -t app.core.database.TORTOISE_ORM
    python -m aerich init-db
else
    echo "Running migrations..."
    python -m aerich upgrade
fi

echo "Starting application..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
