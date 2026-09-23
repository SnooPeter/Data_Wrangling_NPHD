from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set paths
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

file_path = DATA_DIR / "final_airbnb_bond_merged.csv"

# 1. Load dataset
df_airbnb = pd.read_csv(file_path)

# 2. Process Data
df_gap = df_airbnb.dropna(subset=["price", "Median Rent"]).copy()
df_gap["daily_long_term_rent"] = df_gap["Median Rent"] / 7
df_gap["price_gap"] = df_gap["price"] - df_gap["daily_long_term_rent"]

location_gaps = (
    df_gap.groupby("area_code")["price_gap"]
    .agg(["mean", "median", "count"])
    .sort_values(by="median", ascending=False)
)
location_gaps = location_gaps.replace(0, pd.NA)

# 3. Export CSV
csv_output_path = OUTPUT_DIR / "location_price_gaps.csv"
location_gaps.to_csv(csv_output_path)
print(f"Data successfully exported to {csv_output_path}")

# 4. Generate and Save Chart
sns.set_theme(style="whitegrid")
top_10_gaps = location_gaps.head(10).reset_index()

plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=top_10_gaps,
    x="median",
    y=top_10_gaps["area_code"].astype(str),
    palette="Blues_r",
)

plt.title(
    "Top 10 Area Codes by Short- vs. Long-Term Price Gap", fontsize=14, pad=15
)
plt.xlabel("Median Daily Price Gap ($)", fontsize=12)
plt.ylabel("Area Code", fontsize=12)

# Annotate bars with dollar values
for p in ax.patches:
    width = p.get_width()
    ax.annotate(
        f"${width:.2f}",
        (width, p.get_y() + p.get_height() / 2.0),
        ha="left",
        va="center",
        xytext=(5, 0),
        textcoords="offset points",
        fontsize=10,
    )

chart_output_path = OUTPUT_DIR / "top_price_gaps.png"
plt.savefig(chart_output_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Chart successfully saved to {chart_output_path}")