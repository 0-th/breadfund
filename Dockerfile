FROM tiangolo/uvicorn-gunicorn:python3.12-slim

RUN apt-get update && \
    apt-get install -y netcat-openbsd gcc libpq-dev && \
    apt clean && \
    rm -rf /var/cache/apt/*

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8

WORKDIR /app

# Download dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements/prod.txt,target=/tmp/prod.txt \
    python -m pip install -r /tmp/prod.txt

# Copy application files
COPY . .

# Add scripts folder to PATH
ENV PATH "$PATH:/app/scripts"

# Make scripts executable
RUN chmod +x /app/scripts/*

EXPOSE 8000

CMD /app/scripts/start-prod.sh
