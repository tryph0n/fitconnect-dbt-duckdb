"""Run analytics queries from analyses/analytics_queries.sql against the DuckDB database."""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from settings import settings

DB_PATH = PROJECT_ROOT / settings.duckdb_path
QUERIES_FILE = PROJECT_ROOT / "analyses" / "analytics_queries.sql"


def main() -> None:
    if not DB_PATH.exists():
        logger.error("Database not found at %s", DB_PATH)
        logger.error("Run the dbt pipeline first.")
        raise SystemExit(1)

    raw_sql = QUERIES_FILE.read_text()

    # Split on comment lines that start with "-- N." to get individual queries
    queries: list[tuple[str, str]] = []
    current_title = ""
    current_sql_lines: list[str] = []

    for line in raw_sql.splitlines():
        if line.startswith("-- ") and line[3:4].isdigit() and "." in line:
            # Save previous query if any
            if current_sql_lines:
                sql = "\n".join(current_sql_lines).strip()
                if sql:
                    queries.append((current_title, sql))
            current_title = line.lstrip("- ").strip()
            current_sql_lines = []
        elif line.startswith("--"):
            # Skip other comment lines
            continue
        else:
            current_sql_lines.append(line)

    # Don't forget the last query
    if current_sql_lines:
        sql = "\n".join(current_sql_lines).strip()
        if sql:
            queries.append((current_title, sql))

    con = duckdb.connect(str(DB_PATH), read_only=True)

    for title, sql in queries:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
        result = con.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()

        # Print header
        header = " | ".join(f"{col:>20}" for col in columns)
        print(header)
        print("-" * len(header))

        # Print rows
        for row in rows:
            print(" | ".join(f"{str(val):>20}" for val in row))

    con.close()
    print(f"\n{'=' * 60}")
    print("  Analytics complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
