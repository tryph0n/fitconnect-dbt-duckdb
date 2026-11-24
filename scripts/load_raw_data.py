"""Upload CSV files to S3, then load them into PostgreSQL via COPY."""

import logging
import sys
from pathlib import Path

import boto3
import psycopg
from botocore.config import Config
from botocore.exceptions import ClientError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from settings import settings

logger = logging.getLogger(__name__)

INPUT_DIR = PROJECT_ROOT / "data" / "input"

# Parents first for creation, reversed for drops.
LOAD_ORDER = ["users", "profiles", "exercises", "workouts", "workout_exercises"]

TABLE_SCHEMAS = {
    "users": """
        CREATE TABLE users (
            "UserID" INTEGER PRIMARY KEY,
            "Username" TEXT NOT NULL,
            "Email" TEXT NOT NULL,
            "Password" TEXT NOT NULL,
            "JoinDate" DATE,
            "LastLogin" DATE,
            "AccountStatus" TEXT
        )
    """,
    "profiles": """
        CREATE TABLE profiles (
            "ProfileID" INTEGER PRIMARY KEY,
            "UserID" INTEGER NOT NULL,
            "FirstName" TEXT,
            "LastName" TEXT,
            "BirthDate" DATE,
            "Gender" TEXT,
            "Height" NUMERIC(10,2),
            "CurrentWeight" NUMERIC(10,2),
            "TargetWeight" NUMERIC(10,2),
            "FitnessGoal" TEXT,
            "ActivityLevel" TEXT
        )
    """,
    "exercises": """
        CREATE TABLE exercises (
            "ExerciseID" INTEGER PRIMARY KEY,
            "Name" TEXT NOT NULL,
            "Description" TEXT,
            "Category" TEXT,
            "MuscleGroup" TEXT,
            "DifficultyLevel" TEXT,
            "DemoVideoURL" TEXT
        )
    """,
    "workouts": """
        CREATE TABLE workouts (
            "WorkoutID" INTEGER PRIMARY KEY,
            "UserID" INTEGER NOT NULL,
            "WorkoutPlanID" INTEGER,
            "WorkoutDate" DATE,
            "Duration" INTEGER,
            "CaloriesBurned" NUMERIC(10,2),
            "Notes" TEXT,
            "Rating" INTEGER,
            "CompletionStatus" TEXT
        )
    """,
    "workout_exercises": """
        CREATE TABLE workout_exercises (
            "WorkoutID" INTEGER NOT NULL,
            "ExerciseID" INTEGER NOT NULL,
            "SetCount" INTEGER,
            "RepCount" INTEGER,
            "Weight" NUMERIC(10,2),
            "Duration" INTEGER,
            "Notes" TEXT,
            "Order" INTEGER
        )
    """,
}


def make_s3_client():
    """Build the S3 client: a local S3 server if S3_ENDPOINT_URL is set, else AWS S3."""
    endpoint_url = settings.s3_endpoint_url or None
    # moto serves buckets by path, not by virtual host name.
    config = Config(s3={"addressing_style": "path"}) if endpoint_url else None
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
        config=config,
    )


def ensure_bucket(s3_client, bucket: str, region: str) -> None:
    """Create the bucket if it does not exist (the local S3 server starts empty)."""
    if not bucket:
        logger.error("S3_BUCKET is empty: set it in .env (see .env.example)")
        raise SystemExit(1)

    try:
        s3_client.head_bucket(Bucket=bucket)
        logger.info("[skip] s3://%s already exists", bucket)
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise

    create_args = {"Bucket": bucket}
    # us-east-1 is the default region and does not accept a LocationConstraint.
    if region != "us-east-1":
        create_args["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3_client.create_bucket(**create_args)
    logger.info("[create] s3://%s in %s", bucket, region)


def upload_csvs_to_s3(s3_client, bucket: str, prefix: str, input_dir: Path) -> None:
    """Upload local CSVs to S3 (skip if already present)."""
    for table_name in LOAD_ORDER:
        filename = f"{table_name}.csv"
        s3_key = f"{prefix}{filename}"

        # Check if file already exists on S3.
        try:
            s3_client.head_object(Bucket=bucket, Key=s3_key)
            logger.info("[skip] s3://%s/%s already exists", bucket, s3_key)
            continue
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise

        local_path = input_dir / filename
        s3_client.upload_file(str(local_path), bucket, s3_key)
        logger.info("[upload] %s -> s3://%s/%s", local_path.name, bucket, s3_key)


def load_csvs_to_postgres(s3_client, bucket: str, prefix: str, conn) -> None:
    """Download CSVs from S3 and COPY into PostgreSQL tables."""
    # Drop tables in reverse order (children first).
    for table_name in reversed(LOAD_ORDER):
        conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    logger.info("[drop] all tables dropped")

    # Create and load tables in forward order (parents first).
    for table_name in LOAD_ORDER:
        conn.execute(TABLE_SCHEMAS[table_name])
        logger.info("[create] %s", table_name)

        s3_key = f"{prefix}{table_name}.csv"
        response = s3_client.get_object(Bucket=bucket, Key=s3_key)
        csv_data = response["Body"].read()

        with (
            conn.cursor() as cur,
            cur.copy(
                f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')"
            ) as copy,
        ):
            copy.write(csv_data)

        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info("[load] %s: %d rows", table_name, row_count)

    conn.commit()


def main() -> None:
    """Upload CSVs to S3, then load into PostgreSQL."""
    s3_client = make_s3_client()

    logger.info("Step 1: Upload CSVs to S3")
    ensure_bucket(s3_client, settings.s3_bucket, settings.aws_region)
    upload_csvs_to_s3(s3_client, settings.s3_bucket, settings.s3_prefix, INPUT_DIR)

    logger.info("Step 2: Load CSVs from S3 into PostgreSQL")
    with psycopg.connect(settings.pg_url) as conn:
        load_csvs_to_postgres(s3_client, settings.s3_bucket, settings.s3_prefix, conn)

    logger.info("Done.")


if __name__ == "__main__":
    main()
