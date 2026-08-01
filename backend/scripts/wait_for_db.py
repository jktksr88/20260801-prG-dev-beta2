"""Wait for the configured database before running migrations.

Render can provision the web service and Postgres database at nearly the same
moment. A short retry window prevents a transient first connection failure from
terminating the entire deploy.
"""
from __future__ import annotations

import os
import sys
import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.session import engine


def main() -> int:
    attempts = int(os.getenv("DB_WAIT_ATTEMPTS", "90"))
    delay_seconds = float(os.getenv("DB_WAIT_SECONDS", "2"))

    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"Database is ready (attempt {attempt}/{attempts}).", flush=True)
            return 0
        except SQLAlchemyError as exc:
            engine.dispose()
            if attempt == attempts:
                print(
                    f"Database did not become ready after {attempts} attempts: {exc}",
                    file=sys.stderr,
                    flush=True,
                )
                return 1
            print(
                f"Database not ready (attempt {attempt}/{attempts}); retrying in {delay_seconds:g}s.",
                flush=True,
            )
            time.sleep(delay_seconds)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
