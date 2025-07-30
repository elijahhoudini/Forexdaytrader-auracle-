# AURACLE Forex Trading Bot Dockerfile
# Multi-stage build for optimized production container

FROM python:3.11-slim as builder

# Set build arguments
ARG INSTALL_DEV=false

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AURACLE_MODE=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r auracle && useradd -r -g auracle auracle

# Create directories
RUN mkdir -p /app/data /app/logs /app/strategies /app/dashboard && \
    chown -R auracle:auracle /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=auracle:auracle . .

# Create data directories with proper permissions
RUN mkdir -p data/backtests data/logs strategies/custom && \
    chown -R auracle:auracle data strategies

# Switch to non-root user
USER auracle

# Expose ports
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/status', timeout=5)" || exit 1

# Default command (can be overridden)
CMD ["python", "start_forex.py", "--mode", "production"]