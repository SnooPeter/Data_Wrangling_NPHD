"""Deliverable 5, step 2 (SQL version): the same join as merge_datasets.py, done in SQLite.

Original author: Jin.

Running the join in two different tools lets sanity_checks.py confirm that
both give the same result.
"""
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config
from merge_datasets import load_join_inputs

# The ALL/ALL filter sits in the JOIN condition (not WHERE) so that listings
# with no bond match are still kept, as in a pandas left join.
SQL_QUERY = """
SELECT
    a.id, a.name, a.host_id, a.host_name, a.neighbourhood,
    a.latitude, a.longitude, a.room_type, a.price, a.minimum_nights,
    a.number_of_reviews, a.last_review, a.reviews_per_month,
    a.calculated_host_listings_count, a.availability_365,
    a.number_of_reviews_ltm, a.month_year, a.area_code,
    b.TimeFrame, b."Dwelling Type", b."Number Of Beds",
    b."Total Bonds", b."Active Bonds", b."Closed Bonds",
    b."Median Rent", b."Geometric Mean Rent", b."Upper Quartile Rent",
    b."Lower Quartile Rent", b."Log Std Dev Weekly Rent"
FROM airbnb_listings a
LEFT JOIN tenancy_bonds b
    ON a.area_code = b."Location Id"
   AND a.time_key = b.time_key
   AND b."Dwelling Type" = :all_category
   AND b."Number Of Beds" = :all_category;
"""


def main():
    airbnb_df, bond_df = load_join_inputs()

    with closing(sqlite3.connect(config.SQLITE_DB)) as conn:
        airbnb_df.to_sql("airbnb_listings", conn, if_exists="replace", index=False)
        bond_df.to_sql("tenancy_bonds", conn, if_exists="replace", index=False)
        merged_df = pd.read_sql_query(
            SQL_QUERY, conn, params={"all_category": config.ALL_CATEGORY}
        )

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(config.MERGED_SQL, index=False)
    print(f"Saved to: {config.MERGED_SQL}")
    print(f"Merged rows: {len(merged_df):,}")
    print(f"Rows missing Median Rent: {merged_df['Median Rent'].isna().sum():,}")


if __name__ == "__main__":
    main()
