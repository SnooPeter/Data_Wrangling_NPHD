"""Deliverable 5, step 2: join each Airbnb listing-month to its area's bond data for that quarter.

Original author: Jin.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config


def load_join_inputs():
    """Load both tables and add the matching keys (area code + quarter).

    Also used by merge_datasets_sql.py, so both versions of the join use the same keys.
    """
    airbnb_df = pd.read_csv(config.require(config.AIRBNB_WITH_AREA_CODES))
    bond_df = pd.read_csv(config.require(config.BOND_CLEAN))

    airbnb_df["area_code"] = config.clean_area_code(airbnb_df["area_code"])
    bond_df["Location Id"] = config.clean_area_code(bond_df["Location Id"])

    # Monthly snapshots -> quarter keys, so April, May and June all match '2026-04'.
    airbnb_df["time_key"] = config.quarter_key(airbnb_df["month_year"])
    bond_df["time_key"] = bond_df["TimeFrame"].str[:7]  # '2026-04-01' -> '2026-04'
    return airbnb_df, bond_df


def bond_totals(bond_df):
    """Keep one row per area and quarter: the ALL dwelling types / ALL bedrooms total.

    Without this filter each listing would match several bond rows and be duplicated.
    """
    is_total = (bond_df["Dwelling Type"] == config.ALL_CATEGORY) & (
        bond_df["Number Of Beds"] == config.ALL_CATEGORY
    )
    return bond_df[is_total].copy()


def main():
    airbnb_df, bond_df = load_join_inputs()

    # Left join keeps every Airbnb row, including those without bond data.
    merged_df = pd.merge(
        airbnb_df,
        bond_totals(bond_df),
        left_on=["area_code", "time_key"],
        right_on=["Location Id", "time_key"],
        how="left",
        validate="many_to_one",  # raises an error if a bond key is duplicated
    )
    merged_df = merged_df.drop(columns=["Location Id", "time_key"])

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(config.MERGED, index=False)
    print(f"Saved to: {config.MERGED}")
    print(f"Airbnb rows in: {len(airbnb_df):,} | Merged rows out: {len(merged_df):,}")
    print(f"Unique listings: {merged_df['id'].nunique():,}")
    print(f"Rows missing Median Rent: {merged_df['Median Rent'].isna().sum():,}")


if __name__ == "__main__":
    main()
