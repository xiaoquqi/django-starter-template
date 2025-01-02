# Use official Python 3.12 slim image as the base image for the builder stage
FROM python:3.12-slim AS builder

# Set the working directory for builder stage
WORKDIR /app

# Copy all project files into the container
COPY . /app/

# Install build dependencies and virtualenv requirements
RUN mkdir -p /etc/apt/sources.list.d && \
    echo "deb https://mirrors.ustc.edu.cn/debian/ $(grep -oP 'VERSION="[0-9]+ \(\K[^)]+' /etc/os-release) main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian/ $(grep -oP 'VERSION="[0-9]+ \(\K[^)]+' /etc/os-release)-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security $(grep -oP 'VERSION="[0-9]+ \(\K[^)]+' /etc/os-release)-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    git \
    libffi-dev \
    libssl-dev \
    libmariadb-dev \
    pkg-config

# Create a Python virtual environment and install application
RUN pip install virtualenv && \
    virtualenv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install setuptools && \
    cd /app && \
    pip install -r requirements.txt && \
    python setup.py install

# Start final stage with clean Python slim image
FROM python:3.12-slim

# Set working directory for the application
WORKDIR /opt/venv

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/api/docker/entrypoint.sh /
COPY --from=builder /app/api/docker/logratate.conf /etc/logrotate.d/gunicorn

# Install runtime dependencies and configure permissions
RUN apt-get update && \
    apt-get install -y \
        iputils-ping \
        logrotate \
        curl \
        cron \
        libffi-dev \
        libssl-dev \
        libmariadb-dev \
        mariadb-client \
        postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    chmod +x /entrypoint.sh

# Expose port 8000 for Django application
EXPOSE 8000

# Configure cron job to rotate logs every 5 minutes
RUN echo "*/5 * * * * root /usr/sbin/logrotate /etc/logrotate.d/gunicorn" \
    >> /etc/crontab

# Set entrypoint script to handle container startup
ENTRYPOINT ["/entrypoint.sh"]