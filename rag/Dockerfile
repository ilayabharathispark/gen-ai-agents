# Use official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Set working directory
WORKDIR /app

# Install system dependencies (build-essential for potential C-compilations)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Optimize PyTorch: Pre-install the CPU version to avoid downloading the massive CUDA/GPU wheels
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (app.py, ingestion.py, query.py, query_payload.py etc.)
COPY . /app/

# Expose Streamlit default Cloud Run port
EXPOSE 8080

# Run Streamlit, dynamically binding to the port designated by Cloud Run ($PORT)
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
