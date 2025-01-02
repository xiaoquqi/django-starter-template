#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activate virtual environment
VENV_PATH="/opt/venv"
. /opt/venv/bin/activate

PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
DJANGO_BASE_DIR="/opt/venv/lib/python${PYTHON_VERSION}/site-packages/api"
DJANGO_STATIC_TMP_DIR="${DJANGO_BASE_DIR}/core/staticfiles"
DJANGO_STATIC_DIR="/staticfiles"

# Log file paths
LOG_BASE_DIR="/var/log/gunicorn"
ACCESS_LOG="${LOG_BASE_DIR}/gunicorn_access.log"
ERROR_LOG="${LOG_BASE_DIR}/gunicorn_error.log"
CELERY_LOG="${LOG_BASE_DIR}/celery.log"

# Ensure the log directory exists and is writable
mkdir -p $LOG_BASE_DIR
chmod -R 755 $LOG_BASE_DIR

# Use environment variables or defaults
WORKERS=${WORKERS:-4}
THREADS=${THREADS:-4}

# Flower Configurations
REDIS_URL=${REDIS_URL:-redis://redis:6379/0}  # Use environment variable for Redis URL
FLOWER_PORT=5555

echo "Using $WORKERS workers and $THREADS threads."

cd $DJANGO_BASE_DIR
if [[ "$1" == "celery" ]]; then
    # Start Celery worker
    echo "Starting Celery worker..."
    exec celery -A core worker \
        --loglevel="${CELERY_LOG_LEVEL:-info}" \
        --logfile="$CELERY_LOG" \
        --concurrency="$WORKERS"
elif [[ "$1" == "celery-beat" ]]; then
    # Start Celery beat
    echo "Starting Celery beat..."
    exec celery -A core beat \
        --loglevel="${CELERY_LOG_LEVEL:-info}" \
        --logfile="$CELERY_LOG"
elif [[ "$1" == "flower" ]]; then
    # Start Flower for monitoring Celery tasks using the specified broker and port
    echo "Starting Flower..."
    exec celery -A core flower --port=$FLOWER_PORT --broker="$REDIS_URL"
elif [[ "$1" == "gunicorn" ]]; then
    # Begin to check database connection
    DB_TYPE=$(echo "$DATABASE_URL" | awk -F: '{print $1}')
    HOST=$(echo "$DATABASE_URL" | sed -E 's#^[^:]+://[^@]+@([^:/]+).*#\1#')
    PORT=$(echo "$DATABASE_URL" | sed -E 's#.*:([0-9]+).*#\1#')

    echo "Detected DB_TYPE: $DB_TYPE, HOST: $HOST, PORT: ${PORT:-default}"

    while true; do
      case "$DB_TYPE" in
        mysql)
          if mysqladmin ping -h "$HOST" --silent; then
            echo "MySQL is ready!"
            break
          fi
          ;;
        postgres)
          if pg_isready -h "$HOST" -p "${PORT:-5432}" > /dev/null 2>&1; then
            echo "PostgreSQL is ready!"
            break
          fi
          ;;
        *)
          echo "Use SQLite by default and SQLite does not require a health check."
          break
          ;;
      esac
      echo "Waiting for $DB_TYPE at $HOST:$PORT..."
      sleep 2
    done

    # Execute database migrations
    echo "Running migrations..."
    python manage.py migrate --noinput

    # Check if a superuser exists, create one if not
    echo "Checking if superuser exists..."
    DJANGO_SUPERUSER_USERNAME=admin \
    DJANGO_SUPERUSER_EMAIL=admin@example.com \
    DJANGO_SUPERUSER_PASSWORD=adminpassword \
    python manage.py createsuperuser --noinput || echo "Superuser already exists."

    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    cp -rf $DJANGO_STATIC_TMP_DIR/* $DJANGO_STATIC_DIR

    # Start Gunicorn
    echo "Starting Gunicorn..."
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "$WORKERS" \
        --threads "$THREADS" \
        --access-logfile "$ACCESS_LOG" \
        --error-logfile "$ERROR_LOG" \
        --log-level "${GUNICORN_LOG_LEVEL:-info}"
else
    echo "Running command $@"
    exec "$@"
fi
