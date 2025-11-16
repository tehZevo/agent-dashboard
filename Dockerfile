# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create a directory for data persistence
RUN mkdir -p /app/data

# Expose port for Flask app
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command runs the dashboard
# Can be overridden in docker-compose for different services
CMD ["python", "dashboard.py"]
