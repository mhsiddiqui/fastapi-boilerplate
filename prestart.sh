#! /usr/bin/env bash

# Let the DB start
echo "Running backend_pre_start"
python manage.py --command=backend_pre_start

# Run migrations
echo "Running migrations"
alembic upgrade head

# Create initial data in DB
echo "Running initial_data"
python manage.py --command=initial_data
