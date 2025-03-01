# fantasy-football-analytics-v1/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Default command with verbose logging
CMD ["python", "src/data_ingest.py", "--data-file", "/app/data/passing_stats_2022.csv", "--output", "/app/data/cleaned_passing_2022.csv", "--verbose"]