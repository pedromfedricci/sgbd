ARG PYTHON_VERSION="3.14.2"

# Build
FROM python:${PYTHON_VERSION}-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.20 /uv /uvx /bin/

# Disable development dependencies
# Ensure uv commands compile bytecode
ENV UV_NO_DEV=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Runtime
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the python virtual environment
COPY --from=builder /app/.venv ./.venv

# Copy runtime dependencies
COPY scripts/start.sh ./start.sh
COPY alembic.ini ./
COPY alembic ./alembic
COPY ./app ./app

EXPOSE 8000

CMD ["./start.sh"]
