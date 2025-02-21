# Use a small base image with Python 3.11
FROM python:3.11-slim

# Install any OS-level packages you might need
# (In early stages, you might only need minimal or none.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Example: if you need these for building certain Python packages
    build-essential \
    # cURL or other debugging tools can be helpful
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy requirements first to leverage Docker's caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Command to run by default (you can override this)
CMD ["python", "src/data_ingest.py"]
