"""Deliverable 5: sanity checks on the merge step.

Each check prints PASS or FAIL. The script exits with an error if any check
fails, so run_pipeline.py stops before the analysis uses bad data.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

# Weekly median rents outside this range would suggest a wrong column or unit.
PLAUSIBLE_WEEKLY_RENT = (100, 2000)


def run_checks(airbnb, merged, merged_sql):
    """Return a list of (description, passed, detail)."""
    results = []

    # 1. A left join must not add or lose rows.
    results.append((
        "Merge keeps every Airbnb row",
        len(merged) == len(airbnb),
        f"{len(airbnb):,} in, {len(merged):,} out",
    ))

    # 2. One row per listing per snapshot, so no listing was matched to two bond rows.
    duplicates = merged.duplicated(subset=["id", "month_year"]).sum()
    results.append(("No duplicated listing-month rows", duplicates == 0, f"{duplicates} duplicates"))

    # 3. Matched bond rows are the ALL/ALL totals only.
    matched = merged.dropna(subset=["TimeFrame"])
    only_totals = (
        matched["Dwelling Type"].eq(config.ALL_CATEGORY)
        & matched["Number Of Beds"].eq(config.ALL_CATEGORY)
    ).all()
    results.append(("Only ALL/ALL bond totals were joined", only_totals, ""))

    # 4. Each listing was matched to the quarter its snapshot month belongs to.
    wrong_quarter = (config.quarter_key(matched["month_year"]) != matched["TimeFrame"].str[:7]).sum()
    results.append(("Snapshot month matches bond quarter", wrong_quarter == 0, f"{wrong_quarter} mismatches"))

    # 5. Rents are in a believable weekly range.
    low, high = PLAUSIBLE_WEEKLY_RENT
    rents = merged["Median Rent"].dropna()
    results.append((
        f"Median Rent within ${low}-${high} per week",
        rents.between(low, high).all(),
        f"min ${rents.min():.0f}, max ${rents.max():.0f}",
    ))

    # 6. The pandas and SQL versions of the join give identical results.
    key = ["id", "month_year"]
    pandas_rent = merged.set_index(key)["Median Rent"].sort_index()
    sql_rent = merged_sql.set_index(key)["Median Rent"].sort_index()
    results.append((
        "pandas merge and SQL merge agree",
        merged.shape == merged_sql.shape and pandas_rent.equals(sql_rent),
        f"pandas {merged.shape}, SQL {merged_sql.shape}",
    ))
    return results


def main():
    text_keys = {"id": "string", "area_code": "string", "TimeFrame": "string"}
    airbnb = pd.read_csv(config.require(config.AIRBNB_WITH_AREA_CODES), dtype={"id": "string"})
    merged = pd.read_csv(config.require(config.MERGED), dtype=text_keys)
    merged_sql = pd.read_csv(config.require(config.MERGED_SQL), dtype=text_keys)

    results = run_checks(airbnb, merged, merged_sql)
    for description, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {description}" + (f" ({detail})" if detail else ""))

    missing = merged["Median Rent"].isna().mean() * 100
    print(f"\nInfo: {missing:.1f}% of rows have no Median Rent (suppressed by Tenancy Services).")

    failures = [r for r in results if not r[1]]
    if failures:
        sys.exit(f"{len(failures)} sanity check(s) failed.")
    print("All sanity checks passed.")


if __name__ == "__main__":
    main()
