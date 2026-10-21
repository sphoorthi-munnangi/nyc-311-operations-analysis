"""Assess data quality for the 2025 NYC 311 street maintenance dataset."""

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "nyc311_street_2025.csv"

EXPECTED_COLUMNS = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "complaint_type",
    "descriptor",
    "status",
    "borough",
    "incident_zip",
    "resolution_description",
    "open_data_channel_type",
]


def parse_date(value):
    """Parse a NYC 311 timestamp, returning None for blank values."""
    if not value or not value.strip():
        return None

    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def print_counts(title, values):
    """Print frequency counts for a categorical field."""
    print(f"\n{title}")
    print("-" * len(title))

    for value, count in Counter(values).most_common():
        print(f"{value or '[MISSING]'}: {count:,}")


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []

        missing_columns = set(EXPECTED_COLUMNS) - set(columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        rows = list(reader)

    total = len(rows)
    if total == 0:
        raise ValueError("The dataset is empty.")

    print("=" * 55)
    print("NYC 311 STREET MAINTENANCE — DATA QUALITY REPORT")
    print("=" * 55)
    print(f"Total records: {total:,}")
    print(f"Total columns: {len(columns)}")

    print("\nMISSING VALUES BY COLUMN")
    print("-" * 55)

    for column in EXPECTED_COLUMNS:
        missing = sum(
            not row[column] or not row[column].strip()
            for row in rows
        )
        percentage = missing / total * 100
        print(f"{column:<26} {missing:>7,} ({percentage:5.1f}%)")

    ids = [row["unique_key"] for row in rows]
    duplicate_count = len(ids) - len(set(ids))

    print("\nDUPLICATE REQUEST IDs")
    print("-" * 55)
    print(f"Duplicate IDs: {duplicate_count:,}")

    for column in [
        "descriptor",
        "status",
        "borough",
        "open_data_channel_type",
    ]:
        print_counts(
            column.upper().replace("_", " "),
            [row[column].strip() for row in rows],
        )

    invalid_created = 0
    invalid_closed = 0
    closed_before_created = 0
    missing_closed_date = 0
    missing_closed_by_status = Counter()
    created_outside_2025 = 0

    for row in rows:
        created = parse_date(row["created_date"])
        closed = parse_date(row["closed_date"])

        if created is None:
            invalid_created += 1
        elif created.year != 2025:
            created_outside_2025 += 1

        if row["closed_date"].strip():
            if closed is None:
                invalid_closed += 1
        else:
            missing_closed_date += 1
            missing_closed_by_status[row["status"].strip() or "[MISSING]"] += 1

        if created is not None and closed is not None:
            try:
                if closed < created:
                    closed_before_created += 1
            except TypeError:
                invalid_closed += 1

    print("\nDATE QUALITY CHECKS")
    print("-" * 55)
    print(f"Missing or invalid created dates: {invalid_created:,}")
    print(f"Invalid nonblank closed dates: {invalid_closed:,}")
    print(f"Missing closed dates: {missing_closed_date:,}")
    print(f"Closed before created: {closed_before_created:,}")
    print(f"Created outside 2025: {created_outside_2025:,}")

    print_counts(
        "STATUS OF REQUESTS WITHOUT A CLOSED DATE",
        list(missing_closed_by_status.elements()),
    )

    print("\nData quality assessment complete.")


if __name__ == "__main__":
    main()
