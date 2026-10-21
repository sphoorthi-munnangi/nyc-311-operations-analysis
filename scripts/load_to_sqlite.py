"""Build a SQLite database from the cleaned NYC 311 dataset."""

import csv
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = (
    PROJECT_ROOT / "data" / "processed" /
    "nyc311_street_2025_clean.csv"
)

DB_FILE = (
    PROJECT_ROOT / "data" / "processed" /
    "nyc311_operations.db"
)

CREATE_TABLE_SQL = """
CREATE TABLE street_requests (
    unique_key TEXT PRIMARY KEY,
    created_date TEXT NOT NULL,
    closed_date TEXT,
    created_month TEXT NOT NULL,
    agency TEXT NOT NULL,
    complaint_type TEXT NOT NULL,
    descriptor TEXT NOT NULL,
    status TEXT NOT NULL,
    borough TEXT NOT NULL,
    incident_zip TEXT,
    resolution_description TEXT,
    open_data_channel_type TEXT,
    is_closed INTEGER NOT NULL CHECK (is_closed IN (0, 1)),
    is_unresolved INTEGER NOT NULL CHECK (is_unresolved IN (0, 1)),
    has_valid_closure_time INTEGER NOT NULL
        CHECK (has_valid_closure_time IN (0, 1)),
    closure_hours REAL,
    closure_days REAL,
    data_quality_flag TEXT NOT NULL
);
"""

COLUMNS = [
    "unique_key",
    "created_date",
    "closed_date",
    "created_month",
    "agency",
    "complaint_type",
    "descriptor",
    "status",
    "borough",
    "incident_zip",
    "resolution_description",
    "open_data_channel_type",
    "is_closed",
    "is_unresolved",
    "has_valid_closure_time",
    "closure_hours",
    "closure_days",
    "data_quality_flag",
]

INTEGER_COLUMNS = {
    "is_closed",
    "is_unresolved",
    "has_valid_closure_time",
}

REAL_COLUMNS = {
    "closure_hours",
    "closure_days",
}


def convert_row(row):
    """Convert CSV text into appropriate SQLite data types."""
    values = []

    for column in COLUMNS:
        value = row[column].strip()

        if value == "":
            values.append(None)
        elif column in INTEGER_COLUMNS:
            values.append(int(value))
        elif column in REAL_COLUMNS:
            values.append(float(value))
        else:
            values.append(value)

    return tuple(values)


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {CSV_FILE}"
        )

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with CSV_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file has no header.")

        missing = set(COLUMNS) - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        records = [convert_row(row) for row in reader]

    if not records:
        raise ValueError("No records found in the cleaned dataset.")

    placeholders = ", ".join("?" for _ in COLUMNS)
    column_names = ", ".join(COLUMNS)

    insert_sql = (
        f"INSERT INTO street_requests ({column_names}) "
        f"VALUES ({placeholders})"
    )

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("DROP TABLE IF EXISTS street_requests")
        connection.execute(CREATE_TABLE_SQL)
        connection.executemany(insert_sql, records)

        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_descriptor "
            "ON street_requests(descriptor)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_borough "
            "ON street_requests(borough)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_month "
            "ON street_requests(created_month)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_status "
            "ON street_requests(status)"
        )

        total = connection.execute(
            "SELECT COUNT(*) FROM street_requests"
        ).fetchone()[0]

        unique_ids = connection.execute(
            "SELECT COUNT(DISTINCT unique_key) "
            "FROM street_requests"
        ).fetchone()[0]

        closed = connection.execute(
            "SELECT SUM(is_closed) FROM street_requests"
        ).fetchone()[0]

        unresolved = connection.execute(
            "SELECT SUM(is_unresolved) FROM street_requests"
        ).fetchone()[0]

        valid_closure = connection.execute(
            "SELECT SUM(has_valid_closure_time) "
            "FROM street_requests"
        ).fetchone()[0]

        if total != len(records) or unique_ids != total:
            raise RuntimeError(
                "Database validation failed: record count "
                "or unique IDs do not match."
            )

        if total != 51572 or closed != 48430 or unresolved != 3142:
            raise RuntimeError(
                "Database validation failed: unexpected KPI totals."
            )

        if valid_closure != 48424:
            raise RuntimeError(
                "Database validation failed: unexpected "
                "valid closure-time count."
            )

        print("=" * 55)
        print("NYC 311 SQLITE DATABASE VALIDATION")
        print("=" * 55)
        print(f"Imported requests: {total:,}")
        print(f"Unique request IDs: {unique_ids:,}")
        print(f"Closed requests: {closed:,}")
        print(f"Unresolved requests: {unresolved:,}")
        print(f"Valid closure-time records: {valid_closure:,}")
        print(f"Database: {DB_FILE}")
        print("\nDatabase created and validated successfully!")


if __name__ == "__main__":
    main()
