#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating admin if needed..."
python manage.py init_db || true

echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile -