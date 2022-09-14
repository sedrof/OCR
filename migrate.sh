#!/bin/bash

SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"m@gmail.com"}
SUPERUSER_USER_NAME=${DJANGO_SUERUSER_USERNAME:-"m"}
SUPERUSER_USER_PASSWORD=${DJANGO_SUERUSER_PASSWORD:-"admin"}

/opt/venv/bin/python manage.py migrate --noinput
/opt/venv/bin/python manage.py createsuperuser --email $SUPERUSER_EMAIL --username $SUPERUSER_USER_NAME --noinput || true