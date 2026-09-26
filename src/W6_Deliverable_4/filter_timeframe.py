"""Deliverable 4: keep only the bond quarters that overlap the Airbnb snapshots."""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config


def main():
    # Read Location Id as text so values such as NULL and -99 are kept correctly.
    data = pd.read_csv(config.require(config.BOND_RAW), dtype={"Location Id": "string"})

    # The Christchurch data covers October 2025 to June 2026; the bond report is quarterly.
    filtered_data = data[data["TimeFrame"].isin(config.BOND_QUARTERS)].copy()

    config.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    filtered_data.to_csv(config.BOND_TIMEFRAME, index=False)

    print(f"Rows before filtering: {len(data):,}")
    print(f"Rows after filtering: {len(filtered_data):,}")
    print(f"Timeframes kept: {config.BOND_QUARTERS}")
    print(f"Saved to: {config.BOND_TIMEFRAME}")


if __name__ == "__main__":
    main()
