FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .


FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

USER appuser