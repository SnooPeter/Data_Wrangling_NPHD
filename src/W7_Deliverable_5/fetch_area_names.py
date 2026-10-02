"""Deliverable 5: look up the name of every SA2 area in the data (e.g. 322200 -> Rutland).

The bond data only has SA2 codes, so the names come from the same Stats NZ API
as the area codes. One listing location per area is enough: 171 requests
instead of one per listing. Like fetch_area_codes.py it is incremental: names
already saved are reused and only new area codes are queried (--refresh
queries every area again).
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config
from fetch_area_codes import load_api_key, query_many


def saved_area_names():
    """Names found by a previous run (areas without a name are left out, so they are retried)."""
    if not config.SA2_AREA_NAMES.exists():
        return pd.DataFrame(columns=["area_code", "area_name"], dtype="string")
    return pd.read_csv(config.SA2_AREA_NAMES, dtype="string").dropna()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="ignore the saved names and query every area")
    args = parser.parse_args()

    airbnb_df = pd.read_csv(
        config.require(config.AIRBNB_WITH_AREA_CODES), dtype={"area_code": "string"}
    )
    airbnb_df["area_code"] = config.clean_area_code(airbnb_df["area_code"])
    saved = saved_area_names().iloc[0:0] if args.refresh else saved_area_names()

    # One listing location per area code is enough to identify the area.
    sample = airbnb_df.dropna(subset=["area_code"]).drop_duplicates("area_code")
    sample = sample[~sample["area_code"].isin(saved["area_code"])]
    print(f"Areas in data: {airbnb_df['area_code'].nunique()} | Reused: {len(saved)} | To query: {len(sample)}")
    if sample.empty:
        print(f"Nothing new to look up; {config.SA2_AREA_NAMES.name} is up to date.")
        return

    api_key = load_api_key()
    coords = list(sample[["latitude", "longitude"]].itertuples(index=False, name=None))
    areas = query_many(coords, api_key, "Looking up area names")

    names = pd.DataFrame(
        {
            "area_code": sample["area_code"].to_numpy(),
            "area_name": [area.get(config.SA2_2019_NAME_FIELD) if area else None for area in areas],
            "api_code": [area.get(config.SA2_2019_CODE_FIELD) if area else None for area in areas],
        }
    )

    # The same point must fall in the same area it was coded to in step 1.
    mismatched = names["api_code"].notna() & (names["api_code"] != names["area_code"])
    if mismatched.any():
        sys.exit(f"[ERROR] {mismatched.sum()} areas returned a different code than before.")

    missing = names["area_name"].isna().sum()
    if missing:
        print(f"[WARN] {missing} areas did not get a name; charts will show their code instead.")

    names = pd.concat([saved, names.drop(columns="api_code")]).sort_values("area_code")
    names.to_csv(config.SA2_AREA_NAMES, index=False)
    print(f"Found names for {names['area_name'].notna().sum()} of {len(names)} areas")
    print(f"Saved to: {config.SA2_AREA_NAMES}")


if __name__ == "__main__":
    main()
