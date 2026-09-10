# Use official Python runtime image
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr and writing pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Launch ADK Web server on specified Cloud Run port (with optional Memory Bank URI)
CMD ["sh", "-c", "if [ -n \"$MEMORY_SERVICE_URI\" ]; then adk web --host 0.0.0.0 --port ${PORT} --memory_service_uri \"$MEMORY_SERVICE_URI\"; else adk web --host 0.0.0.0 --port ${PORT}; fi"]

