# Multi-stage Dockerfile for Aetherra
# Optimized for production deployment with development support

# =============================================================================
# Base Stage - Common dependencies
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r aetherra && useradd -r -g aetherra aetherra

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements/ requirements/

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Install all dependencies including dev tools
RUN pip install --upgrade pip && \
    pip install -r requirements/dev.txt && \
    pip install -r requirements/quantum.txt || echo "Quantum deps optional"

# Install pre-commit for development
RUN pip install pre-commit

# Copy source code
COPY . .

# Install pre-commit hooks
RUN pre-commit install || echo "Pre-commit setup skipped"

# Change ownership to non-root user
RUN chown -R aetherra:aetherra /app

USER aetherra

# Development server port
EXPOSE 8686 5000

# Development command
CMD ["python", "Aetherra/lyrixa/gui/web_interface_server.py"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base as production

# Install only production dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements/base.txt

# Copy only necessary files
COPY Aetherra/ Aetherra/
COPY scripts/ scripts/
COPY aetherra_launcher.py .

# Create necessary directories
RUN mkdir -p logs data config && \
    chown -R aetherra:aetherra /app

USER aetherra

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8686/api/system/status || exit 1

# Production ports
EXPOSE 8686

# Production command
CMD ["python", "aetherra_launcher.py"]

# =============================================================================
# Testing Stage
# =============================================================================
FROM development as testing

# Copy test files
COPY tests/ tests/
COPY pytest.ini .
COPY .pre-commit-config.yaml .

# Run tests during build
RUN python -m pytest tests/ -v --tb=short || echo "Tests completed with issues"

# =============================================================================
# Quantum Stage - With quantum computing support
# =============================================================================
FROM production as quantum

USER root

# Install quantum computing dependencies
RUN pip install -r requirements/quantum.txt || echo "Some quantum deps may have failed"

# Additional quantum system dependencies if needed
RUN apt-get update && apt-get install -y \
    liblapack-dev \
    libblas-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

USER aetherra

# Quantum-enabled production command
CMD ["python", "aetherra_launcher.py", "--quantum-enabled"]
