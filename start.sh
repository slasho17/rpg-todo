#!/usr/bin/env bash
set -e
python manage.py migrate
python manage.py collectstatic --noinput
# create superuser if missing (ignore if exists)
python manage.py createsuperuser --noinput || true
gunicorn core.wsgi:application --bind 0.0.0.0:${PORT}
