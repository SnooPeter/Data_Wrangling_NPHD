"""Deliverable 3: build one Christchurch dataset from the monthly Inside Airbnb snapshots.

Steps
1. Load each monthly NZ listings.csv (Oct 2025 - Jun 2026) from data/raw/.
2. Keep Christchurch City listings only.
3. Add a month_year column (e.g. 'Oct 2025') saying which snapshot the row came from.
4. Concatenate all months into one dataset -> data/interim/concatenate_chch.csv.
5. Summary statistics for every column -> output/W5_Deliverable_3/:
   - numeric columns: count, mean, std, min, median, max
   - text columns: number of categories and the most common values with counts
   - date columns: earliest and latest date
   - missing values per column (count and %)
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

# ID columns are labels, not quantities, so a mean or std of them is meaningless.
ID_COLUMNS = ["id", "host_id"]
# Free-text columns have almost one value per row, so category counts are not useful.
FREE_TEXT_COLUMNS = ["name"]
DATE_COLUMNS = ["last_review"]
TOP_CATEGORIES = 10


def snapshot_files():
    """Return (path, 'Mon YYYY') for each expected monthly snapshot, in date order."""
    files = []
    missing = []
    for year_month in config.AIRBNB_SNAPSHOT_MONTHS:
        path = config.RAW_DIR / f"listings_{year_month}.csv"
        if path.exists():
            files.append((path, config.month_label(year_month)))
        else:
            missing.append(path.name)

    if missing:
        raise FileNotFoundError(
            f"Missing Airbnb snapshots in {config.RAW_DIR}: {', '.join(missing)}\n"
            "Download each month's NZ listings.csv from Inside Airbnb and save it as "
            "listings_YYYY-MM.csv (see README)."
        )
    return files


def load_christchurch_snapshot(path, month_year):
    """Load one NZ snapshot, keep Christchurch City only and label the month."""
    df = pd.read_csv(path)
    df = df[df["neighbourhood_group"] == config.CITY].copy()
    df["month_year"] = month_year
    print(f"  {path.name}: {len(df):,} Christchurch listings ({month_year})")
    return df


def missing_value_summary(df):
    return pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_percent": (df.isna().mean() * 100).round(2),
        }
    ).sort_values("missing_count", ascending=False)


def numeric_summary(df):
    # Completely empty columns (e.g. license) have no statistics; they appear in the missing-values table.
    numeric_columns = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c]) and c not in ID_COLUMNS and df[c].notna().any()
    ]
    summary = df[numeric_columns].agg(["count", "mean", "std", "min", "median", "max"]).T
    return summary.round(2)


def date_summary(df):
    rows = []
    for column in DATE_COLUMNS:
        dates = pd.to_datetime(df[column], errors="coerce")
        rows.append({"column": column, "min": dates.min().date(), "max": dates.max().date()})
    return pd.DataFrame(rows).set_index("column")


def categorical_summary(df):
    """Long table: column, category, count - the most common categories of each text column."""
    text_columns = [
        c for c in df.columns
        if not pd.api.types.is_numeric_dtype(df[c])
        and c not in FREE_TEXT_COLUMNS + DATE_COLUMNS
    ]
    rows = []
    for column in text_columns:
        counts = df[column].value_counts(dropna=False)
        for category, count in counts.head(TOP_CATEGORIES).items():
            rows.append(
                {
                    "column": column,
                    "n_categories": df[column].nunique(),
                    "category": "(missing)" if pd.isna(category) else category,
                    "count": count,
                }
            )
    return pd.DataFrame(rows)


def main():
    print(f"Loading snapshots from {config.RAW_DIR}")
    christchurch = pd.concat(
        [load_christchurch_snapshot(path, label) for path, label in snapshot_files()],
        ignore_index=True,
    )

    config.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    christchurch.to_csv(config.CHCH_CONCAT, index=False)
    print(f"\nCombined dataset: {christchurch.shape[0]:,} rows x {christchurch.shape[1]} columns")
    print(f"Unique listings: {christchurch['id'].nunique():,} | Unique hosts: {christchurch['host_id'].nunique():,}")
    print(f"Saved to: {config.CHCH_CONCAT}")

    summaries = {
        "missing_values": missing_value_summary(christchurch),
        "numeric_summary": numeric_summary(christchurch),
        "date_summary": date_summary(christchurch),
        "categorical_summary": categorical_summary(christchurch),
    }

    config.D3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, table in summaries.items():
        table.to_csv(config.D3_OUTPUT_DIR / f"{name}.csv", index=name != "categorical_summary")

    with pd.option_context("display.width", 120, "display.max_columns", 10):
        print("\n=== Missing values per column ===")
        print(summaries["missing_values"])
        print("\n=== Numeric columns ===")
        print(summaries["numeric_summary"])
        print("\n=== Date columns ===")
        print(summaries["date_summary"])
        print("\n=== Text columns (number of categories) ===")
        print(summaries["categorical_summary"].groupby("column")["n_categories"].first())

    print(f"\nSummary tables saved to: {config.D3_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
