# Multi-stage Dockerfile for FastAPI Bug Tracker Backend
# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies only needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels in isolated directory
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Runtime (Lightweight)
FROM python:3.13-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install Python packages from wheels (no compilation needed, faster)
RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
