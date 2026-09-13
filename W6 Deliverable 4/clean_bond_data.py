from pathlib import Path

import pandas as pd


# Use paths relative to this file.
folder = Path(__file__).parent
input_file = folder / "data" / "bond_data_timeframe.csv"
output_file = folder / "data" / "bond_data_clean.csv"


data = pd.read_csv(input_file, dtype={"Location Id": "string"})
starting_rows = len(data)


# A row without a Location Id cannot be matched to a location, so remove it.
missing_location_id = data["Location Id"].isna().sum()
data = data.dropna(subset=["Location Id"]).copy()


# Make dates and numeric columns consistent.
data["TimeFrame"] = pd.to_datetime(data["TimeFrame"], errors="coerce")

number_columns = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent",
]

for column in number_columns:
    data[column] = pd.to_numeric(data[column], errors="coerce")


# Number Of Beds stays as text because it includes values such as ALL and 5+.
data.to_csv(output_file, index=False, date_format="%Y-%m-%d")

print("Bond data cleaning finished")
print(f"Rows: {starting_rows} -> {len(data)}")
print(f"Rows removed because Location Id was missing: {missing_location_id}")
print(f"Saved to: {output_file}")
