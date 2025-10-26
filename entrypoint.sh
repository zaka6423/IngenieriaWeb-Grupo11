#!/usr/bin/env bash
set -e

PORT="${PORT:-8000}"

echo ">> Migrando DB en /data/db.sqlite3 ..."
python manage.py migrate --noinput

echo ">> Collectstatic en /app/staticfiles ..."
python manage.py collectstatic --noinput

echo ">> Iniciando Gunicorn en 0.0.0.0:${PORT}"
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT}
