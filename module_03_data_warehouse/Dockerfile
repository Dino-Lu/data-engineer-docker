FROM python:3.11-slim

WORKDIR /app

# Install certificates (important for HTTPS)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install --no-cache-dir \
    google-cloud-storage \
    requests

# Copy your script
COPY scripts/ ./scripts/

CMD ["python", "scripts/load_yellow_taxi_data.py"]