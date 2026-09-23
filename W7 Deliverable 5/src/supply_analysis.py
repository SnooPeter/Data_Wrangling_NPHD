from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# Set paths
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

file_path = DATA_DIR / "final_airbnb_bond_merged.csv"

# 1. Load merged dataset
df_merged = pd.read_csv(file_path)

# 2. Aggregate Data
airbnb_counts = (
    df_merged.groupby("area_code")["id"]
    .nunique()
    .reset_index(name="airbnb_count")
)

bond_counts = (
    df_merged.groupby("area_code")["Active Bonds"]
    .max()
    .reset_index(name="long_term_rentals")
)

supply_comparison = pd.merge(
    airbnb_counts, bond_counts, on="area_code", how="outer"
)

supply_comparison["total_supply"] = (
    supply_comparison["airbnb_count"] + supply_comparison["long_term_rentals"]
)

supply_comparison["airbnb_ratio"] = (
    supply_comparison["airbnb_count"] / supply_comparison["total_supply"] * 100
)

supply_comparison = supply_comparison.replace(0, pd.NA)
supply_comparison = supply_comparison.sort_values(
    by="airbnb_count", ascending=False
)

# 3. Export CSV
csv_output_path = OUTPUT_DIR / "airbnb_vs_longterm_supply.csv"
supply_comparison.to_csv(csv_output_path, index=False)
print(f"File exported successfully to: {csv_output_path}")

# 4. Generate and Save Stacked Bar Chart
top_10_supply = supply_comparison.sort_values(
    by="total_supply", ascending=False
).head(10)

plt.figure(figsize=(12, 6))

plt.bar(
    top_10_supply["area_code"].astype(str),
    top_10_supply["long_term_rentals"],
    label="Long-Term Rentals",
    color="#2b5c8f",
)

plt.bar(
    top_10_supply["area_code"].astype(str),
    top_10_supply["airbnb_count"],
    bottom=top_10_supply["long_term_rentals"],
    label="Airbnb Listings",
    color="#ff5a5f",
)

plt.title(
    "Housing Supply Breakdown: Airbnb vs. Long-Term Rentals (Top 10 Areas)",
    fontsize=14,
    pad=15,
)
plt.xlabel("Area Code", fontsize=12)
plt.ylabel("Number of Units", fontsize=12)
plt.legend(title="Rental Type")
plt.xticks(rotation=45)

chart_output_path = OUTPUT_DIR / "supply_comparison_stacked.png"
plt.savefig(chart_output_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Chart successfully saved to {chart_output_path}")