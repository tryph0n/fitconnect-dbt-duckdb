FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen

# Copy project
COPY dbt_project.yml profiles.yml settings.py ./
COPY data/input/ data/input/
COPY scripts/ scripts/
COPY models/ models/
COPY analyses/ analyses/

# Default: run the full pipeline (load data, build models, generate docs)
CMD ["sh", "-c", "uv run python scripts/load_raw_data.py && uv run dbt build --profiles-dir . && uv run dbt docs generate --profiles-dir ."]
