FROM python:3.13

WORKDIR /app

# Copy only dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install system dependencies and create user in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir poetry && \
    groupadd -r appgroup && \
    useradd -r -g appgroup -u 1000 appuser && \
    mkdir -p /var/log/app && \
    touch /var/log/info.log && \
    chown -R appuser:appgroup /var/log/app /var/log/info.log

# Configure poetry and install dependencies
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONPATH=/app

# Install dependencies
RUN poetry install --no-interaction --with database

# Copy application code
COPY . /app/
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "analyzerservice.src.main:app", "--host", "0.0.0.0", "--port", "8000"]