# fantasy-football-analytics-v1/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# CMD removed, will be specified in docker-compose.yml or at runtime