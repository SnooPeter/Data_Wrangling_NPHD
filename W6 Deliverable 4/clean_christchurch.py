from pathlib import Path

import pandas as pd


# The paths are relative to this file, so the script works from different
# folders as long as the repository structure stays the same.
folder = Path(__file__).parent
input_file = folder.parent / "Concatenate_Chch_Data" / "concatenate_chch.csv"
output_folder = folder / "data"
output_file = output_folder / "christchurch_listings_clean.csv"


# Read the data from Deliverable 3.
data = pd.read_csv(input_file, dtype={"id": "string", "host_id": "string"})
starting_rows = len(data)


# These columns are not useful for the later comparison:
# license is completely empty and neighbourhood_group is always Christchurch.
data = data.drop(columns=["license", "neighbourhood_group"])


# Keep rows with missing values instead of filling them with made-up values.
# Missing prices can be excluded later when calculating rental prices.
missing_prices = data["price"].isna().sum()
missing_reviews = data["last_review"].isna().sum()

# Make the main numeric and date columns consistent.
number_columns = [
    "latitude",
    "longitude",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
    "number_of_reviews_ltm",
]

for column in number_columns:
    data[column] = pd.to_numeric(data[column], errors="coerce")

data["last_review"] = pd.to_datetime(data["last_review"], errors="coerce")


# Do not remove duplicate IDs. The same listing appears in more than one month,
# and each monthly snapshot is needed for comparisons over time.
output_folder.mkdir(exist_ok=True)
data.to_csv(output_file, index=False, date_format="%Y-%m-%d")


print("Cleaning finished")
print(f"Rows: {starting_rows} -> {len(data)}")
print(f"Columns: {len(data.columns)}")
print(f"Rows with missing price: {missing_prices}")
print(f"Rows with missing last review: {missing_reviews}")
print(f"Saved to: {output_file}")
