"""Deliverable 5, Q3: Airbnb listings vs long-term rentals in each area.

Airbnb supply = unique listings seen in any snapshot (Oct 2025 - Jun 2026).
Long-term supply = highest Active Bonds value for the area in the three quarters.
Note: the two counts cover different time windows (see design_principles.md).
Original author: Nic (table and chart were previously two separate scripts).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

CSV_OUTPUT = config.D5_OUTPUT_DIR / "airbnb_vs_longterm_supply.csv"
CHART_OUTPUT = config.D5_OUTPUT_DIR / "supply_comparison_stacked.png"


def supply_by_area(df):
    grouped = df.groupby("area_code")
    supply = pd.DataFrame(
        {
            "airbnb_count": grouped["id"].nunique(),
            "long_term_rentals": grouped["Active Bonds"].max(),
        }
    ).reset_index()

    supply["total_supply"] = supply["airbnb_count"] + supply["long_term_rentals"]
    supply["airbnb_ratio"] = supply["airbnb_count"] / supply["total_supply"] * 100
    return supply.sort_values(by="airbnb_count", ascending=False, kind="stable")


def plot_top_supply(supply):
    # Areas without bond data have no total, so they cannot be ranked here.
    top = supply.dropna(subset=["total_supply"]).nlargest(config.TOP_N, "total_supply")
    area_labels = top["area_code"].astype(str)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(area_labels, top["long_term_rentals"], label="Long-Term Rentals", color="#2b5c8f")
    ax.bar(
        area_labels,
        top["airbnb_count"],
        bottom=top["long_term_rentals"],
        label="Airbnb Listings",
        color="#ff5a5f",
    )
    ax.set_title(
        f"Housing Supply Breakdown: Airbnb vs. Long-Term Rentals (Top {config.TOP_N} Areas)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Area Code", fontsize=12)
    ax.set_ylabel("Number of Units", fontsize=12)
    ax.legend(title="Rental Type")
    ax.tick_params(axis="x", rotation=45)
    fig.savefig(CHART_OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = pd.read_csv(config.require(config.MERGED), dtype={"area_code": "string"})
    supply = supply_by_area(df)

    config.D5_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    supply.to_csv(CSV_OUTPUT, index=False)
    plot_top_supply(supply)

    print(supply.head(config.TOP_N).to_string(index=False))
    print(f"Saved to: {CSV_OUTPUT}")
    print(f"Saved to: {CHART_OUTPUT}")


if __name__ == "__main__":
    main()
