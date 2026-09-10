FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Optional: keep build-essential only if a package compiles C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first to avoid wheel/resolver bugs
RUN pip install --no-cache-dir --upgrade pip

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user for secure runtime execution
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Use 'exec' so adk receives SIGTERM for graceful shutdown on Cloud Run
CMD ["sh", "-c", "if [ -n \"$MEMORY_SERVICE_URI\" ]; then exec adk web --host 0.0.0.0 --port ${PORT} --memory_service_uri \"$MEMORY_SERVICE_URI\"; else exec adk web --host 0.0.0.0 --port ${PORT}; fi"]