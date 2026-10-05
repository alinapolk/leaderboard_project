#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

# Ждём, пока PostgreSQL поднимется
while ! nc -z db 5432; do
  sleep 0.5
done

echo "PostgreSQL started!"

echo "Waiting for Redis..."

# Ждём, пока Redis поднимется
while ! nc -z redis 6379; do
  sleep 0.5
done

echo "Redis started!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."

# Выполняем команду, переданную в CMD
exec "$@"