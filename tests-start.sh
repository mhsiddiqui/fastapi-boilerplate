#! /usr/bin/env bash
set -e

python manage.py --command=tests_pre_start

bash ./scripts/test.sh "$@"
