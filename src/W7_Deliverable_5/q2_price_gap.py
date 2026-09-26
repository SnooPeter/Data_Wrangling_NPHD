"""Deliverable 5, Q2: which areas have the largest gap between Airbnb and long-term rent?

Gap = Airbnb nightly price - (weekly median rent / 7), summarised per area.
Original author: Nic (table and chart were previously two separate scripts).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

CSV_OUTPUT = config.D5_OUTPUT_DIR / "location_price_gaps.csv"
CHART_OUTPUT = config.D5_OUTPUT_DIR / "top_price_gaps.png"


def price_gaps_by_area(df):
    gap = df.dropna(subset=["price", "Median Rent"]).copy()
    gap["daily_long_term_rent"] = gap["Median Rent"] / config.DAYS_PER_WEEK
    gap["price_gap"] = gap["price"] - gap["daily_long_term_rent"]

    return (
        gap.groupby("area_code")["price_gap"]
        .agg(["mean", "median", "count"])
        .sort_values(by="median", ascending=False, kind="stable")  # stable: same tie order on every pandas version
    )


def plot_top_gaps(location_gaps):
    top = location_gaps.head(config.TOP_N).iloc[::-1]  # largest bar at the top

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top.index.astype(str), top["median"], color="#2b5c8f")
    ax.bar_label(bars, labels=[f"${v:.2f}" for v in top["median"]], padding=5, fontsize=10)
    ax.set_title(
        f"Top {config.TOP_N} Area Codes by Short- vs. Long-Term Price Gap", fontsize=14, pad=15
    )
    ax.set_xlabel("Median Daily Price Gap ($)", fontsize=12)
    ax.set_ylabel("Area Code", fontsize=12)
    ax.grid(axis="x", alpha=0.3)
    fig.savefig(CHART_OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = pd.read_csv(config.require(config.MERGED), dtype={"area_code": "string"})
    location_gaps = price_gaps_by_area(df)

    config.D5_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    location_gaps.to_csv(CSV_OUTPUT)
    plot_top_gaps(location_gaps)

    print("Top Locations with the Largest Short- vs. Long-Term Price Gap:")
    print(location_gaps.head(config.TOP_N))
    print(f"Saved to: {CSV_OUTPUT}")
    print(f"Saved to: {CHART_OUTPUT}")


if __name__ == "__main__":
    main()
