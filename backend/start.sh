#!/bin/sh
set -e

cd /app

echo "=== Railway start.sh boshlandi ==="
echo "PORT=${PORT:-8000}"
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}"

echo "=== Django check ==="
python manage.py check --deploy || true

echo "=== Migrations ==="
python manage.py migrate --noinput

echo "=== Init DB / Admin ==="
python manage.py init_db

echo "=== Starting Gunicorn ==="
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${WEB_CONCURRENCY:-1} \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
