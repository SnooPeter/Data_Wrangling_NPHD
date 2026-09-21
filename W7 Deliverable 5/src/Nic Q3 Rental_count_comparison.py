from pathlib import Path
import pandas as pd

# Define paths dynamically
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# 3. Merge counts together
supply_comparison = pd.merge(
    airbnb_counts, bond_counts, on="area_code", how="outer"
)

# Calculate total supply
supply_comparison["total_supply"] = (
    supply_comparison["airbnb_count"]
    + supply_comparison["long_term_rentals"]
)

# Calculate Airbnb percentage
supply_comparison["airbnb_ratio"] = (
    supply_comparison["airbnb_count"]
    / supply_comparison["total_supply"]
    * 100
)

# Change zeros to NA
supply_comparison = supply_comparison.replace(0, pd.NA)

print(
    supply_comparison.sort_values(by="airbnb_count", ascending=False).head(10)
)

# Sort results
supply_comparison = supply_comparison.sort_values(
    by="airbnb_count", ascending=False
)

print(supply_comparison.head(10))

# Export to CSV inside the output directory
output_file = OUTPUT_DIR / "airbnb_vs_longterm_supply.csv"
supply_comparison.to_csv(output_file, index=False)

print(f"File exported successfully to: {output_file}")