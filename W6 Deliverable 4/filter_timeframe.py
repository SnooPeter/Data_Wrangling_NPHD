from pathlib import Path

import pandas as pd


# Use paths relative to this file.
folder = Path(__file__).parent
input_file = (
    folder.parent
    / "Data"
    / "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"
)
output_file = folder / "data" / "bond_data_timeframe.csv"


# The Christchurch data covers October 2025 to June 2026.
# The bond report is quarterly, so these are the matching quarters.
timeframes_to_keep = [
    "2025-10-01",
    "2026-01-01",
    "2026-04-01",
]


# Read Location Id as text so values such as NULL and -99 are kept correctly.
data = pd.read_csv(input_file, dtype={"Location Id": "string"})
filtered_data = data[data["TimeFrame"].isin(timeframes_to_keep)].copy()

filtered_data.to_csv(output_file, index=False)

print(f"Rows before filtering: {len(data)}")
print(f"Rows after filtering: {len(filtered_data)}")
print(f"Timeframes kept: {timeframes_to_keep}")
print(f"Saved to: {output_file}")
