"""Deliverable 5, Q1: median nightly Airbnb price in Christchurch Central (SA2 326600).

Original author: Nic.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config


def main():
    df = pd.read_csv(config.require(config.MERGED), dtype={"area_code": "string"})
    central = df[df["area_code"] == config.CHRISTCHURCH_CENTRAL_SA2]

    # Each row is one listing in one monthly snapshot (listings can appear up to 9 times).
    median_price = central["price"].median()

    print(f"Median Airbnb Price in Christchurch Central: ${median_price:.2f}")
    print(
        f"Based on {central['price'].notna().sum():,} listing-month rows with a price "
        f"({central['id'].nunique():,} unique listings)"
    )


if __name__ == "__main__":
    main()
