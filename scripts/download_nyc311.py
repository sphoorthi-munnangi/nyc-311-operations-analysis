"""Download and validate NYC 311 street maintenance requests for 2025."""

import csv
import io
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
JSON_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "nyc311_street_2025.csv"

WHERE = (
    "created_date >= '2025-01-01T00:00:00' "
    "AND created_date < '2026-01-01T00:00:00' "
    "AND agency = 'DOT' "
    "AND complaint_type = 'Street Condition' "
    "AND descriptor IN ('Pothole', 'Cave-in', 'Failed Street Repair')"
)

FIELDS = [
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

BATCH_SIZE = 10000


def fetch(url, parameters):
    """Fetch API data with retries for temporary network failures."""
    full_url = url + "?" + urlencode(parameters)

    for attempt in range(1, 4):
        try:
            request = Request(
                full_url,
                headers={"User-Agent": "NYC311-Portfolio-Analysis/1.0"},
            )
            with urlopen(request, timeout=120) as response:
                return response.read().decode("utf-8-sig")
        except (HTTPError, URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code in (400, 401, 403, 404):
                raise RuntimeError(f"API request failed: {error}") from error
            if attempt == 3:
                raise RuntimeError(f"API request failed: {error}") from error
            print(f"Temporary API error; retrying ({attempt}/3)...")
            time.sleep(attempt * 3)

    raise RuntimeError("API request failed after retries")


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    count_response = fetch(
        JSON_URL,
        {"$select": "count(*) as total", "$where": WHERE},
    )
    expected_count = int(json.loads(count_response)[0]["total"])
    print(f"API reports {expected_count:,} matching requests.")

    rows = []
    offset = 0

    while True:
        csv_text = fetch(
            API_URL,
            {
                "$select": ",".join(FIELDS),
                "$where": WHERE,
                "$order": "unique_key ASC",
                "$limit": BATCH_SIZE,
                "$offset": offset,
            },
        )

        batch = list(csv.DictReader(io.StringIO(csv_text)))

        if not batch:
            break

        rows.extend(batch)
        offset += len(batch)
        print(f"Downloaded {len(rows):,} records...")

        if len(batch) < BATCH_SIZE:
            break

    if len(rows) != expected_count:
        raise RuntimeError(
            f"Record count mismatch: expected {expected_count:,}, "
            f"downloaded {len(rows):,}. Dataset not saved."
        )

    ids = [row["unique_key"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate request IDs detected. Dataset not saved.")

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("\nValidation successful!")
    print(f"Total records: {len(rows):,}")
    print(f"Unique request IDs: {len(set(ids)):,}")

    for descriptor, count in sorted(
        Counter(row["descriptor"] for row in rows).items()
    ):
        print(f"{descriptor}: {count:,}")

    print(f"Downloaded at (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
