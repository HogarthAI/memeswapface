#!/bin/sh
set -e

# Apply migrations
alembic upgrade head

# Запуск приложения
exec python src/main.py
