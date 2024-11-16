ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc libpq-dev && \
    apt clean && \
    rm -rf /var/cache/apt/*

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8

WORKDIR /app

# Create a non-privileged user
ARG UID=1000
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements/prod.txt,target=/tmp/prod.txt \
    python -m pip install -r /tmp/prod.txt

# Copy application files
COPY . .

# Fix permissions for appuser
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod +x /app/scripts/*

# Add scripts folder to PATH
ENV PATH "$PATH:/app/scripts"

# Now switch to non-root user
USER appuser

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD /app/scripts/start-prod.sh
