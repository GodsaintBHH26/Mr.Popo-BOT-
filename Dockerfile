# Use a supported Debian-based Python image (Bullseye = Debian 11, still supported)
# Alternatively, use python:3.11-slim-bookworm for a newer Python + Debian 12
FROM python:3.9-slim-bullseye

# Install Tesseract OCR, English language pack, and OpenCV dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start command
CMD ["python", "main.py"]