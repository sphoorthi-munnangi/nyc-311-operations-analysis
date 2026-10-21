"""Clean NYC 311 street maintenance data for reproducible analysis."""

import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "nyc311_street_2025.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "nyc311_street_2025_clean.csv"

VALID_BOROUGHS = {
    "BRONX",
    "BROOKLYN",
    "MANHATTAN",
    "QUEENS",
    "STATEN ISLAND",
}

VALID_DESCRIPTORS = {
    "Pothole",
    "Cave-in",
    "Failed Street Repair",
}

OUTPUT_COLUMNS = [
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


def parse_timestamp(value):
    """Parse a timestamp, returning None for missing or invalid values."""
    value = (value or "").strip()

    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clean_row(row):
    """Transform one request without discarding its original information."""
    cleaned = {
        column: (row.get(column) or "").strip()
        for column in [
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
    }

    created = parse_timestamp(cleaned["created_date"])
    closed = parse_timestamp(cleaned["closed_date"])

    if created is None:
        raise ValueError(
            f"Missing or invalid creation date: {cleaned['unique_key']}"
        )

    if not (datetime(2025, 1, 1) <= created < datetime(2026, 1, 1)):
        raise ValueError(
            f"Creation date outside 2025: {cleaned['unique_key']}"
        )

    if cleaned["descriptor"] not in VALID_DESCRIPTORS:
        raise ValueError(
            f"Unexpected descriptor: {cleaned['unique_key']}"
        )

    cleaned["borough"] = cleaned["borough"].upper() or "UNSPECIFIED"

    if cleaned["borough"] not in VALID_BOROUGHS:
        cleaned["borough"] = "UNSPECIFIED"

    cleaned["status"] = cleaned["status"].title() or "Unspecified"

    cleaned["incident_zip"] = cleaned["incident_zip"] or ""

    cleaned["open_data_channel_type"] = (
        cleaned["open_data_channel_type"].upper() or "UNKNOWN"
    )

    cleaned["created_month"] = created.strftime("%Y-%m")

    is_closed = cleaned["status"] == "Closed"
    cleaned["is_closed"] = int(is_closed)
    cleaned["is_unresolved"] = int(not is_closed)

    flags = []
    duration_hours = None

    if cleaned["closed_date"] and closed is None:
        flags.append("INVALID_CLOSED_DATE")

    if closed is not None:
        try:
            duration_hours = (closed - created).total_seconds() / 3600
        except TypeError:
            flags.append("INCOMPATIBLE_TIMEZONES")

    if duration_hours is not None and duration_hours < 0:
        flags.append("NEGATIVE_CLOSURE_DURATION")

    if not is_closed and cleaned["closed_date"]:
        flags.append("NON_CLOSED_WITH_CLOSURE_DATE")

    if is_closed and not cleaned["closed_date"]:
        flags.append("CLOSED_WITHOUT_CLOSURE_DATE")

    valid_closure = (
        is_closed
        and duration_hours is not None
        and duration_hours >= 0
    )

    cleaned["has_valid_closure_time"] = int(valid_closure)

    if valid_closure:
        cleaned["closure_hours"] = round(duration_hours, 4)
        cleaned["closure_days"] = round(duration_hours / 24, 6)
    else:
        cleaned["closure_hours"] = ""
        cleaned["closure_days"] = ""

    cleaned["data_quality_flag"] = (
        "|".join(flags) if flags else "OK"
    )

    return cleaned


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Raw dataset not found: {INPUT_FILE}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter()
    ids = set()

    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")

        missing = set(OUTPUT_COLUMNS[:3] + OUTPUT_COLUMNS[4:12]) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing source columns: {sorted(missing)}")

        with OUTPUT_FILE.open(
            "w", newline="", encoding="utf-8"
        ) as destination:
            writer = csv.DictWriter(
                destination,
                fieldnames=OUTPUT_COLUMNS,
            )
            writer.writeheader()

            for row in reader:
                cleaned = clean_row(row)

                request_id = cleaned["unique_key"]

                if not request_id:
                    raise ValueError("Found a missing request ID.")

                if request_id in ids:
                    raise ValueError(f"Duplicate request ID: {request_id}")

                ids.add(request_id)
                writer.writerow(cleaned)

                counts["total"] += 1
                counts["closed"] += cleaned["is_closed"]
                counts["unresolved"] += cleaned["is_unresolved"]
                counts["valid_closure"] += cleaned[
                    "has_valid_closure_time"
                ]

                for flag in cleaned["data_quality_flag"].split("|"):
                    counts[f"flag:{flag}"] += 1

    print("=" * 55)
    print("NYC 311 DATA CLEANING SUMMARY")
    print("=" * 55)
    print(f"Total requests preserved: {counts['total']:,}")
    print(f"Closed requests: {counts['closed']:,}")
    print(f"Unresolved requests: {counts['unresolved']:,}")
    print(
        "Valid closure-time records: "
        f"{counts['valid_closure']:,}"
    )

    print("\nDATA QUALITY FLAGS")
    for key, count in sorted(counts.items()):
        if key.startswith("flag:"):
            print(f"{key.removeprefix('flag:')}: {count:,}")

    print(f"\nSaved cleaned dataset to: {OUTPUT_FILE}")
    print(
        "Processing completed (UTC): "
        f"{datetime.now(timezone.utc).isoformat()}"
    )


if __name__ == "__main__":
    main()
