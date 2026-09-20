from pathlib import Path
import pandas as pd

# Path to the directory where this script resides
SCRIPT_DIR = Path(__file__).resolve().parent

# Path to the data folder (one level up if script is in scripts/, or same level)
# If script and data folder are both in the project root:
DATA_DIR = SCRIPT_DIR / "data"

# File path
file_path = DATA_DIR / "final_airbnb_bond_merged.csv"

# Load dataset
df_airbnb = pd.read_csv(file_path)

# Drop rows missing price or long-term rent info
df_gap = df_airbnb.dropna(subset=["price", "Median Rent"]).copy()

# Compute daily long-term rent rate and price gap
df_gap["daily_long_term_rent"] = df_gap["Median Rent"] / 7
df_gap["price_gap"] = df_gap["price"] - df_gap["daily_long_term_rent"]

# Group by location / area code to find the largest gap
location_gaps = (
    df_gap.groupby("area_code")["price_gap"]
    .agg(["mean", "median", "count"])
    .sort_values(by="median", ascending=False)
)

print("Top Locations with the Largest Short- vs. Long-Term Price Gap:")
print(location_gaps.head(10))