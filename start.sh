#!/usr/bin/env bash
set -e
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_initial_superuser
python manage.py ensure_site_and_social     # <-- novo: garante SITE e vínculo do Google
gunicorn core.wsgi:application --bind 0.0.0.0:${PORT}
