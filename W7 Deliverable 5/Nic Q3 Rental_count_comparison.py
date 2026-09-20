from pathlib import Path
import pandas as pd

# Define paths dynamically
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"  # Adjust if files are in the same folder as script
file_path = DATA_DIR / "final_airbnb_bond_merged.csv"

# Load merged dataset
df_merged = pd.read_csv(file_path)

# 1. Count distinct Airbnb listings per area code
airbnb_counts = (
    df_merged.groupby("area_code")["id"]
    .nunique()
    .reset_index(name="airbnb_count")
)

# 2. Extract long-term rental active bond counts per area code
bond_counts = (
    df_merged.groupby("area_code")["Active Bonds"]
    .max()
    .reset_index(name="long_term_rentals")
)

# 3. Merge counts together for comparison
supply_comparison = pd.merge(
    airbnb_counts, bond_counts, on="area_code", how="outer"
).fillna(0)

# Calculate total supply and ratio of short-term supply safely
supply_comparison["total_supply"] = (
    supply_comparison["airbnb_count"] + supply_comparison["long_term_rentals"]
)

# Use fillna(0) in case total_supply is 0
supply_comparison["airbnb_ratio"] = (
    (supply_comparison["airbnb_count"] / supply_comparison["total_supply"])
    * 100
).fillna(0)

# Display top 10 locations by Airbnb volume
print(
    supply_comparison.sort_values(
        by="airbnb_count", ascending=False
    ).head(10)
)