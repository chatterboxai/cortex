FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /cortex

# Install libpq-dev for llamaindex with postgres chat store integration
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

# Make sure celery and fastapi is in PATH
RUN ln -s /cortex/.venv/bin/celery /usr/local/bin/celery
RUN ln -s /cortex/.venv/bin/fastapi /usr/local/bin/fastapi

# Copy application code
COPY ./app ./app

# Set environment variables
ENV PYTHONPATH=/cortex \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=PROD

# Expose port for the FastAPI application
EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]