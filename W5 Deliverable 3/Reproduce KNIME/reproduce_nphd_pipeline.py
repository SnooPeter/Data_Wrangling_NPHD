"""
Reproduce the KNIME NPHD pipeline analysis in Python.

1. Price histogram — All NZ vs Christchurch City, combined in one chart
2. Days-since-last-review histogram
3. Top 10% most-reviewed listings — All NZ vs Christchurch City count

Input: listings_for_W5.csv (Inside Airbnb, New Zealand, June 2026 snapshot)
"""

import pandas as pd
import matplotlib.pyplot as plt

INPUT_PATH = "listings_for_W5.csv"
REFERENCE_DATE = pd.Timestamp("2026-06-16")
KEEP_COLS = ["name", "neighbourhood_group", "price", "number_of_reviews", "last_review"]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[KEEP_COLS]


def price_histogram(df: pd.DataFrame):
    priced = df.dropna(subset=["price"]).copy()
    priced = priced[priced["price"] <= 2000]

    all_nz = priced.copy()
    all_nz["area"] = "All NZ"

    christchurch = priced[priced["neighbourhood_group"] == "Christchurch City"].copy()
    christchurch["area"] = "Christchurch City"

    combined = pd.concat([all_nz, christchurch], ignore_index=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    bins = range(0, 2001, 100)
    for area, color in [("All NZ", "#4C72B0"), ("Christchurch City", "#DD8452")]:
        subset = combined[combined["area"] == area]
        ax.hist(subset["price"], bins=bins, alpha=0.6, label=area, color=color)
    ax.set_xlabel("Price ($NZD)")
    ax.set_ylabel("Number of listings")
    ax.set_title("Price Distribution — All NZ vs Christchurch City")
    ax.legend()
    fig.tight_layout()
    fig.savefig("price_histogram.png", dpi=150)
    plt.close(fig)


def days_since_last_review_histogram(df: pd.DataFrame):
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
    fig.savefig("days_since_last_review_histogram.png", dpi=150)
    plt.close(fig)


def top_10_percent_reviews(df: pd.DataFrame):
    sorted_df = df.sort_values("number_of_reviews", ascending=False).copy()
    sorted_df["rank"] = sorted_df["number_of_reviews"].rank(method="min", ascending=False)

    threshold = len(sorted_df) * 0.1
    top_10_pct = sorted_df[sorted_df["rank"] <= threshold]

    all_nz_count = len(top_10_pct)
    christchurch_count = (top_10_pct["neighbourhood_group"] == "Christchurch City").sum()

    print()
    print(f"New Zealand Top 10%: {all_nz_count}")
    print(f"Christchurch Top 10%: {christchurch_count}")
    print()


if __name__ == "__main__":
    data = load_data(INPUT_PATH)
    price_histogram(data)
    days_since_last_review_histogram(data)
    top_10_percent_reviews(data)