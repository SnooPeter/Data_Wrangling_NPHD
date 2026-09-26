"""Deliverable 4: clean the filtered bond data (location IDs, dates, numeric columns)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

NUMBER_COLUMNS = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent",
]


def main():
    data = pd.read_csv(config.require(config.BOND_TIMEFRAME), dtype={"Location Id": "string"})
    starting_rows = len(data)

    # A row without a Location Id cannot be matched to a location, so remove it.
    missing_location_id = data["Location Id"].isna().sum()
    data = data.dropna(subset=["Location Id"])
    # -99 rows aggregate several locations rather than describing one area.
    aggregate_rows = (data["Location Id"] == "-99").sum()
    data = data[data["Location Id"] != "-99"].copy()

    # Make dates and numeric columns consistent.
    data["TimeFrame"] = pd.to_datetime(data["TimeFrame"], errors="coerce")
    for column in NUMBER_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Number Of Beds stays as text because it includes values such as ALL and 5+.
    data.to_csv(config.BOND_CLEAN, index=False, date_format="%Y-%m-%d")

    print("Bond data cleaning finished")
    print(f"Rows: {starting_rows:,} -> {len(data):,}")
    print(f"Rows removed because Location Id was missing: {missing_location_id}")
    print(f"Rows removed because Location Id was -99: {aggregate_rows}")
    print(f"Saved to: {config.BOND_CLEAN}")


if __name__ == "__main__":
    main()
