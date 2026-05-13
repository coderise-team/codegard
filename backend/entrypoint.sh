#!/bin/bash
set -e

python django_app/manage.py migrate --noinput

exec "$@"
