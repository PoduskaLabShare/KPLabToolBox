# syntax=docker/dockerfile:1.4

# Use a lightweight and modern Python image
FROM python:3.11

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

# Set a working directory
WORKDIR /app

# Copy and install dependencies first for better layer caching
COPY --link requirements.txt .
RUN uv pip install -r requirements.txt

# Copy your application source files
COPY --link CorrelationPlotter.py .
COPY --link NoPlot.png .

# Expose the port
EXPOSE 8080

# Create a non-root user for security
RUN useradd -m app_user \
    && mkdir -p /app/__marimo__/cache \
    && chown -R app_user:app_user /app

# Switch to non-root user
USER app_user

# Run your app with configurable host and port
CMD ["marimo", "run", "CorrelationPlotter.py", "--host", "0.0.0.0", "-p", "8080"]
