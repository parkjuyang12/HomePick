#!/bin/sh
set -e

echo "PostgreSQL started successfully!"

echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate --no-input

if [ -f "initial_data.json" ]; then
  echo "Loading initial data fixtures..."
  python manage.py loaddata initial_data.json
else
  echo "No initial data fixture found. Skipping data loading."
fi

echo "Starting Django server..."
exec "$@"
