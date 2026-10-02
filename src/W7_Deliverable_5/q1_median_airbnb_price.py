"""Deliverable 5, Q1: median nightly Airbnb price in Christchurch Central (SA2 326600).

Original author: Nic.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

CSV_OUTPUT = config.D5_OUTPUT_DIR / "q1_median_airbnb_price.csv"


def main():
    df = pd.read_csv(config.require(config.MERGED), dtype={"area_code": "string"})
    central = df[df["area_code"] == config.CHRISTCHURCH_CENTRAL_SA2]

    # Each row is one listing in one monthly snapshot (listings can appear once per month).
    median_price = central["price"].median()

    result = pd.DataFrame(
        {
            "area_code": [config.CHRISTCHURCH_CENTRAL_SA2],
            "median_price": [median_price],
            "listing_month_rows": [central["price"].notna().sum()],
            "unique_listings": [central["id"].nunique()],
            "months": [config.snapshot_range_label()],
        }
    )
    config.D5_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(CSV_OUTPUT, index=False)

    print(f"Median Airbnb Price in Christchurch Central: ${median_price:.2f}")
    print(
        f"Based on {result['listing_month_rows'][0]:,} listing-month rows with a price "
        f"({result['unique_listings'][0]:,} unique listings)"
    )
    print(f"Saved to: {CSV_OUTPUT}")


if __name__ == "__main__":
    main()
