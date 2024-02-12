#! /usr/bin/env bash
set -e

python manage.py --command=celeryworker_pre_start

celery -A app.worker worker -l info -Q main-queue -c 1
