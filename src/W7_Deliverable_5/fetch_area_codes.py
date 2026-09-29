"""Deliverable 5, step 1: add an SA2-2019 area code to every Airbnb listing (Stats NZ API).

Original author: Jin.

This is the only step that needs the internet and an API key: put
STATS_NZ_API_KEY=... in a .env file at the project root (see .env.example).
The result is saved, so run_pipeline.py skips this step when it already exists.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

API_URL = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"
# A known central Christchurch point used to test the key before the full run.
TEST_POINT = (-43.51108, 172.62388)
# The work is waiting on the network, so threads are enough; keep the number
# small so we do not flood the Stats NZ API.
MAX_WORKERS = 8
REQUEST_TIMEOUT_SECONDS = 10


def load_api_key():
    """Read STATS_NZ_API_KEY from the root .env file and check that it works."""
    load_dotenv(config.ENV_FILE)
    api_key = os.getenv("STATS_NZ_API_KEY")
    if not api_key:
        sys.exit(
            f"[ERROR] STATS_NZ_API_KEY not found. Copy .env.example to {config.ENV_FILE} "
            "and add your Stats NZ Datafinder key."
        )

    print("Testing API connection with SA2 2019 layer...")
    test_area = query_sa2(*TEST_POINT, api_key)
    if not test_area:
        sys.exit("[ERROR] API test failed. Check your API key in .env and your internet connection.")
    print(f"API connection successful. Test area: {test_area[config.SA2_2019_NAME_FIELD]}")
    return api_key


def query_sa2(lat, lon, api_key, layer_id=config.SA2_2019_LAYER_ID):
    """Return the SA2-2019 area containing (lat, lon) as a dict of its properties
    (code, name, size), or None if it cannot be found."""
    params = {"key": api_key, "layer": layer_id, "x": lon, "y": lat}
    try:
        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as error:
        tqdm.write(f"[WARN] API request failed for ({lat}, {lon}): {error}")
        return None

    features = (
        response.json()
        .get("vectorQuery", {})
        .get("layers", {})
        .get(str(layer_id), {})
        .get("features", [])
    )
    return features[0]["properties"] if features else None


def query_many(coords, api_key, description):
    """Query a list of (lat, lon) pairs in parallel, with a progress bar."""
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = pool.map(lambda c: query_sa2(c[0], c[1], api_key), coords)
        return list(tqdm(results, total=len(coords), desc=description, unit="request"))


def main():
    api_key = load_api_key()
    airbnb_df = pd.read_csv(config.require(config.CHCH_CLEAN))

    # Many rows share a location, so query each unique coordinate pair only once.
    coords = list(
        airbnb_df[["latitude", "longitude"]]
        .dropna()
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    print(f"Total rows: {len(airbnb_df):,} | Unique locations to query: {len(coords):,}")

    areas = query_many(coords, api_key, "Looking up area codes")
    coord_lookup = {
        coord: area.get(config.SA2_2019_CODE_FIELD) if area else None
        for coord, area in zip(coords, areas)
    }

    airbnb_df["area_code"] = [
        coord_lookup.get((lat, lon))
        for lat, lon in zip(airbnb_df["latitude"], airbnb_df["longitude"])
    ]

    unmatched = airbnb_df["area_code"].isna().sum()
    if unmatched:
        print(f"[WARN] {unmatched:,} rows did not get an area code.")

    airbnb_df.to_csv(config.AIRBNB_WITH_AREA_CODES, index=False)
    print(f"Saved to: {config.AIRBNB_WITH_AREA_CODES}")


if __name__ == "__main__":
    main()
