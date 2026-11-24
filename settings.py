"""Centralized project settings loaded from .env via pydantic-settings."""

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # DuckDB / dbt
    duckdb_path: str = "data/fitconnect.duckdb"
    docs_port: int = 8080
    analytics_schema: str = "analytics"
    dbt_threads: int = 4

    # PostgreSQL (used by Python code / psycopg)
    pg_user: str = "postgres"
    pg_password: str = "changeme"
    pg_host: str = "postgres"
    pg_port: int = 5432
    pg_db: str = "fitconnect"

    # Docker PostgreSQL (read by the postgres:16 image)
    postgres_user: str = "postgres"
    postgres_password: str = "changeme"
    postgres_db: str = "fitconnect"

    # S3: an endpoint URL targets a local S3 server (moto); empty means real AWS S3
    s3_endpoint_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "eu-west-3"
    s3_bucket: str = ""
    s3_prefix: str = "fitconnect/"

    @property
    def pg_url(self) -> str:
        """Build the PostgreSQL connection URL."""
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )


settings = Settings()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
