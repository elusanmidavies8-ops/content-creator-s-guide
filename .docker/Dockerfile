# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Non-root user (uid 1000, typical dev uid)
RUN useradd --create-home --uid 1000 postwise

WORKDIR /app

# Copy dependency manifest first (layer caching — code changes don't
# invalidate the dep install)
COPY pyproject.toml ./
COPY README.md ./

# Use uv for fast, reproducible installs
RUN pip install --no-cache-dir uv \
 && uv pip install --system --no-cache .

# Copy source
COPY src/ ./src/
COPY postwise_ui.py ./

# Drop privileges
USER postwise

# Gradio default port
EXPOSE 7860

# Gradio env for container-friendly launch
ENV GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

CMD ["python", "postwise_ui.py"]