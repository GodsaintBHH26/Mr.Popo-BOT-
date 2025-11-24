# Use an official Python runtime as a parent image
# Choose a Python version that matches your requirements.
# python:3.9-slim-buster is a good choice for Debian-based systems.
FROM python:3.9-slim-buster

# Install Tesseract OCR and its English language pack
# `tesseract-ocr` is the main package, `tesseract-ocr-eng` for English language data.
# `libgl1-mesa-glx` is a common dependency for OpenCV in headless environments, though
# `opencv-python-headless` might not strictly require it, it's good for robustness.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Command to run your application
# This can also be defined in railway.toml's [start] section
CMD ["python", "main.py"]