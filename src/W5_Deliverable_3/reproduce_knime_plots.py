"""Deliverable 3: reproduce the Deliverable 2 KNIME analysis in Python (June 2026 NZ snapshot).

1. Price histogram - All NZ vs Christchurch City, combined in one chart
2. Days-since-last-review histogram
3. Top 10% most-reviewed listings - All NZ vs Christchurch City count (printed)
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

INPUT_PATH = config.RAW_DIR / "listings_2026-06.csv"
REFERENCE_DATE = pd.Timestamp("2026-06-16")  # date of the June 2026 snapshot
KEEP_COLS = ["name", "neighbourhood_group", "price", "number_of_reviews", "last_review"]
MAX_PRICE = 2000  # same cut-off as the KNIME workflow


def load_data(path):
    return pd.read_csv(config.require(path))[KEEP_COLS]


def price_histogram(df):
    priced = df.dropna(subset=["price"])
    priced = priced[priced["price"] <= MAX_PRICE]
    christchurch = priced[priced["neighbourhood_group"] == config.CITY]

    fig, ax = plt.subplots(figsize=(9, 5))
    bins = range(0, MAX_PRICE + 1, 100)
    ax.hist(priced["price"], bins=bins, alpha=0.6, label="All NZ", color="#4C72B0")
    ax.hist(christchurch["price"], bins=bins, alpha=0.6, label=config.CITY, color="#DD8452")
    ax.set_xlabel("Price ($NZD)")
    ax.set_ylabel("Number of listings")
    ax.set_title("Price Distribution — All NZ vs Christchurch City")
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.D3_OUTPUT_DIR / "price_histogram.png", dpi=150)
    plt.close(fig)


def days_since_last_review_histogram(df):
    reviewed = df.dropna(subset=["last_review"]).copy()
    reviewed["last_review"] = pd.to_datetime(reviewed["last_review"])
    reviewed["days_since_last_review"] = (REFERENCE_DATE - reviewed["last_review"]).dt.days

    fig, ax = plt.subplots(figsize=(9, 5))
    custom_bins = [0, 30, 60, 90, 180, 365, 999]
    ax.hist(reviewed["days_since_last_review"], bins=custom_bins, color="#55A868")
    ax.set_xticks(custom_bins)
    ax.set_xlabel("Days since last review")
    ax.set_ylabel("Number of listings")
    ax.set_title("Distribution of Days Since Last Review")
    fig.tight_layout()
    fig.savefig(config.D3_OUTPUT_DIR / "days_since_last_review_histogram.png", dpi=150)
    plt.close(fig)


def top_10_percent_reviews(df):
    ranked = df.copy()
    ranked["rank"] = ranked["number_of_reviews"].rank(method="min", ascending=False)
    top_10_pct = ranked[ranked["rank"] <= len(ranked) * 0.1]

    print(f"New Zealand Top 10%: {len(top_10_pct)}")
    print(f"Christchurch Top 10%: {(top_10_pct['neighbourhood_group'] == config.CITY).sum()}")


def main():
    config.D3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data(INPUT_PATH)
    price_histogram(data)
    days_since_last_review_histogram(data)
    top_10_percent_reviews(data)
    print(f"Plots saved to: {config.D3_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
