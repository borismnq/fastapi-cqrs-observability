#!/bin/bash
set -e

echo "Initializing database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=postgres psql -h localhost -U postgres -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - initializing Aerich"

# Initialize Aerich (only first time)
if [ ! -d "migrations" ]; then
    aerich init -t app.core.database.TORTOISE_ORM
    aerich init-db
fi

# Run migrations
aerich upgrade

echo "Database initialized successfully!"
