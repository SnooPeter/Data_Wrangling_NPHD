"""Deliverable 4: clean the concatenated Christchurch Airbnb listings."""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

NUMBER_COLUMNS = [
    "latitude",
    "longitude",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
    "number_of_reviews_ltm",
]


def main():
    data = pd.read_csv(
        config.require(config.CHCH_CONCAT), dtype={"id": "string", "host_id": "string"}
    )
    starting_rows = len(data)

    # license is completely empty and neighbourhood_group is always Christchurch.
    data = data.drop(columns=["license", "neighbourhood_group"])

    # Keep rows with missing values instead of filling them with made-up values.
    # Missing prices are excluded later, only in analyses that use price.
    missing_prices = data["price"].isna().sum()
    missing_reviews = data["last_review"].isna().sum()

    for column in NUMBER_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["last_review"] = pd.to_datetime(data["last_review"], errors="coerce")

    # Do not remove duplicate IDs. The same listing appears in more than one month,
    # and each monthly snapshot is needed for comparisons over time.
    data.to_csv(config.CHCH_CLEAN, index=False, date_format="%Y-%m-%d")

    print("Cleaning finished")
    print(f"Rows: {starting_rows:,} -> {len(data):,}")
    print(f"Columns: {len(data.columns)}")
    print(f"Rows with missing price: {missing_prices:,}")
    print(f"Rows with missing last review: {missing_reviews:,}")
    print(f"Saved to: {config.CHCH_CLEAN}")


if __name__ == "__main__":
    main()
