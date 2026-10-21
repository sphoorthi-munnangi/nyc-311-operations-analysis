"""Advanced operational analysis of NYC 311 street maintenance requests."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "nyc311_street_2025_clean.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SNAPSHOT_DATE = pd.Timestamp("2026-10-21", tz="UTC")

BOROUGH_ORDER = [
    "BRONX",
    "BROOKLYN",
    "MANHATTAN",
    "QUEENS",
    "STATEN ISLAND",
]

CATEGORY_ORDER = [
    "Pothole",
    "Cave-in",
    "Failed Street Repair",
]


def save_chart(filename):
    """Save a publication-ready chart."""
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Chart saved: {filename}")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={"unique_key": str, "incident_zip": str},
        low_memory=False,
    )

    if len(df) != 51572 or df["unique_key"].duplicated().any():
        raise ValueError("Dataset count or unique request IDs are invalid.")

    df["created_date"] = pd.to_datetime(
        df["created_date"], errors="raise", utc=True
    )
    df["closure_days"] = pd.to_numeric(
        df["closure_days"], errors="coerce"
    )

    print("=" * 60)
    print("NYC 311 ADVANCED OPERATIONS ANALYSIS")
    print("=" * 60)
    print(f"Requests analyzed: {len(df):,}")

    # Analysis 1: Unresolved requests by borough.
    unresolved = df[df["is_unresolved"] == 1].copy()

    unresolved_by_borough = (
        unresolved.groupby("borough")
        .size()
        .reset_index(name="unresolved_requests")
        .sort_values("unresolved_requests", ascending=False)
    )

    unresolved_by_borough.to_csv(
        OUTPUT_DIR / "unresolved_by_borough.csv", index=False
    )

    print("\nUNRESOLVED REQUESTS BY BOROUGH")
    print(unresolved_by_borough.to_string(index=False))

    plt.figure(figsize=(10, 5))
    sns.barplot(
        data=unresolved_by_borough,
        x="unresolved_requests",
        y="borough",
        color="#2878B5",
    )
    plt.title("Unresolved 2025 Street Maintenance Requests by Borough")
    plt.xlabel("Requests not marked Closed at extraction")
    plt.ylabel("Borough")
    save_chart("unresolved_by_borough.png")

    # Analysis 2: Age of unresolved requests as of extraction date.
    # This measures time since creation, NOT proven continuous backlog age.
    unresolved["age_days_at_snapshot"] = (
        SNAPSHOT_DATE - unresolved["created_date"]
    ).dt.total_seconds() / 86400

    if (unresolved["age_days_at_snapshot"] < 0).any():
        raise ValueError("Snapshot date precedes a request creation date.")

    age_summary = (
        unresolved.groupby("borough")
        .agg(
            unresolved_requests=("unique_key", "count"),
            median_age_days=("age_days_at_snapshot", "median"),
            mean_age_days=("age_days_at_snapshot", "mean"),
        )
        .reset_index()
        .sort_values("unresolved_requests", ascending=False)
    )

    age_summary[
        ["median_age_days", "mean_age_days"]
    ] = age_summary[
        ["median_age_days", "mean_age_days"]
    ].round(1)

    age_summary.to_csv(
        OUTPUT_DIR / "unresolved_age_by_borough.csv", index=False
    )

    print("\nUNRESOLVED REQUEST AGE BY BOROUGH")
    print(age_summary.to_string(index=False))

    # Analysis 3: Category-adjusted borough comparison.
    valid = df[df["has_valid_closure_time"] == 1].copy()
    valid = valid[valid["borough"].isin(BOROUGH_ORDER)]

    borough_category = (
        valid.groupby(["borough", "descriptor"])
        .agg(
            closed_requests=("unique_key", "count"),
            median_closure_days=("closure_days", "median"),
            mean_closure_days=("closure_days", "mean"),
        )
        .reset_index()
    )

    borough_category[
        ["median_closure_days", "mean_closure_days"]
    ] = borough_category[
        ["median_closure_days", "mean_closure_days"]
    ].round(2)

    borough_category.to_csv(
        OUTPUT_DIR / "closure_time_by_borough_category.csv",
        index=False,
    )

    print("\nCLOSURE TIMES BY BOROUGH AND CATEGORY")
    print(borough_category.to_string(index=False))

    pivot = borough_category.pivot(
        index="borough",
        columns="descriptor",
        values="median_closure_days",
    ).reindex(index=BOROUGH_ORDER, columns=CATEGORY_ORDER)

    plt.figure(figsize=(10, 5))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        linewidths=0.5,
        cbar_kws={"label": "Median administrative closure (days)"},
    )
    plt.title("Median Closure Time by Borough and Maintenance Category")
    plt.xlabel("Maintenance category")
    plt.ylabel("Borough")
    save_chart("closure_time_borough_category_heatmap.png")

    # Analysis 4: Long-running administrative closures.
    valid["over_7_days"] = valid["closure_days"] > 7

    long_running = (
        valid.groupby(["borough", "descriptor"])
        .agg(
            eligible_closed_requests=("unique_key", "count"),
            requests_over_7_days=("over_7_days", "sum"),
        )
        .reset_index()
    )

    long_running["over_7_days_pct"] = (
        100
        * long_running["requests_over_7_days"]
        / long_running["eligible_closed_requests"]
    ).round(2)

    long_running.to_csv(
        OUTPUT_DIR / "long_running_closures.csv", index=False
    )

    print("\nCLOSURES TAKING MORE THAN SEVEN DAYS")
    print(
        long_running.sort_values(
            "over_7_days_pct", ascending=False
        ).to_string(index=False)
    )

    # Analysis 5: Queens unresolved requests by creation month.
    queens_unresolved = unresolved[
        unresolved["borough"] == "QUEENS"
    ]

    queens_monthly = (
        queens_unresolved.groupby("created_month")
        .size()
        .reset_index(name="unresolved_requests")
        .sort_values("created_month")
    )

    queens_monthly.to_csv(
        OUTPUT_DIR / "queens_unresolved_by_month.csv", index=False
    )

    plt.figure(figsize=(11, 5))
    sns.barplot(
        data=queens_monthly,
        x="created_month",
        y="unresolved_requests",
        color="#2878B5",
    )
    plt.title("Queens Unresolved Requests by 2025 Creation Month")
    plt.xlabel("Request creation month")
    plt.ylabel("Requests not marked Closed at extraction")
    plt.xticks(rotation=45)
    save_chart("queens_unresolved_by_month.png")

    print("\nQUEENS UNRESOLVED REQUESTS BY CREATION MONTH")
    print(queens_monthly.to_string(index=False))

    print("\nAnalysis completed successfully.")
    print(f"Outputs saved to: {OUTPUT_DIR}")
    print(
        "Interpretation note: status and unresolved age are based "
        "on the October 21, 2026 extraction snapshot."
    )


if __name__ == "__main__":
    main()
