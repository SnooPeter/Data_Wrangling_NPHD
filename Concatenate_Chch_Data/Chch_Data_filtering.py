from pathlib import Path

import pandas as pd


# Resolve data files relative to this script, not the terminal's working directory.
DATA_DIR = Path(__file__).resolve().parent

# Files in chronological order (Oct 2025 -> Jun 2026)
files = [
    ("listings (8).csv", "Oct 2025"),
    ("listings (7).csv", "Nov 2025"),
    ("listings (6).csv", "Dec 2025"),
    ("listings (5).csv", "Jan 2026"),
    ("listings (4).csv", "Feb 2026"),
    ("listings (3).csv", "Mar 2026"),
    ("listings (2).csv", "Apr 2026"),
    ("listings (1).csv", "May 2026"),
    ("listings.csv", "Jun 2026")
]

all_data = []
for file, month_year in files:
    df = pd.read_csv(DATA_DIR / file)

    # Filter for Christchurch City
    df = df[df["neighbourhood_group"] == "Christchurch City"].copy()

    # Add snapshot month and year as a single column
    df["month_year"] = month_year

    all_data.append(df)

christchurch_data = pd.concat(all_data, ignore_index=True)

print(christchurch_data.shape)

# Save the combined dataset
output_path = DATA_DIR / "concatenate_chch.csv"
christchurch_data.to_csv(output_path, index=False)

print(f"{output_path.name} has been created successfully at {output_path}.")
