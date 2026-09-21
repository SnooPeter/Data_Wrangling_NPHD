from pathlib import Path
import pandas as pd

# Path to the directory where this script resides
SCRIPT_DIR = Path(__file__).resolve().parent

# Path to the data folder
DATA_DIR = SCRIPT_DIR.parent / "data"

# File path
file_path = DATA_DIR / "final_airbnb_bond_merged.csv"

# Load dataset
df_airbnb = pd.read_csv(file_path)

# Drop rows missing price or long-term rent info
df_gap = df_airbnb.dropna(
    subset=["price", "Median Rent"]
).copy()

# Compute daily long-term rent rate and price gap
df_gap["daily_long_term_rent"] = df_gap["Median Rent"] / 7
df_gap["price_gap"] = (
    df_gap["price"] - df_gap["daily_long_term_rent"]
)

# Group by area code
location_gaps = (
    df_gap.groupby("area_code")["price_gap"]
    .agg(["mean", "median", "count"])
    .sort_values(by="median", ascending=False)
)

# Change zeros to NA
location_gaps = location_gaps.replace(0, pd.NA)

print("Top Locations with the Largest Short- vs. Long-Term Price Gap:")
print(location_gaps.head(10))

# Path to the output directory
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

# Create the output folder if it doesn't already exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define the full output file path
output_path = OUTPUT_DIR / "location_price_gaps.csv"

# Export the DataFrame to CSV
location_gaps.to_csv(output_path)

print(f"Data successfully exported to {output_path}")