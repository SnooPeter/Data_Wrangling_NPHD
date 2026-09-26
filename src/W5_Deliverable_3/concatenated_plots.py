"""Deliverable 3: KNIME-style plots for the concatenated Christchurch dataset (Oct 2025 - Jun 2026)."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets this file find src/config.py
import config

REFERENCE_DATE = pd.Timestamp("2026-06-16")  # date of the latest (June 2026) snapshot
MAX_PRICE = 2000


def price_histogram(df):
    priced = df.dropna(subset=["price"])
    priced = priced[priced["price"] <= MAX_PRICE]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(priced["price"], bins=range(0, MAX_PRICE + 1, 100), color="#DD8452")
    ax.set_xlabel("Price ($NZD)")
    ax.set_ylabel("Number of records")
    ax.set_title("Price Distribution — Christchurch City")
    fig.tight_layout()
    fig.savefig(config.D3_OUTPUT_DIR / "price_histogram_concatenated.png", dpi=150)
    plt.close(fig)


def days_since_last_review_histogram(df):
    reviewed = df.dropna(subset=["last_review"]).copy()
    reviewed["days_since_last_review"] = (REFERENCE_DATE - reviewed["last_review"]).dt.days
    reviewed = reviewed[reviewed["days_since_last_review"].between(0, 999)]

    fig, ax = plt.subplots(figsize=(9, 5))
    review_bins = [0, 30, 60, 90, 180, 365, 999]
    ax.hist(reviewed["days_since_last_review"], bins=review_bins, color="#55A868")
    ax.set_xticks(review_bins)
    ax.set_xlabel("Days since last review")
    ax.set_ylabel("Number of records")
    ax.set_title("Distribution of Days Since Last Review")
    fig.tight_layout()
    fig.savefig(config.D3_OUTPUT_DIR / "days_since_last_review_concatenated.png", dpi=150)
    plt.close(fig)


def top_10_percent_reviews(df):
    ranked = df.dropna(subset=["number_of_reviews"]).copy()
    ranked["rank"] = ranked["number_of_reviews"].rank(method="min", ascending=False)
    top_10_percent = ranked[ranked["rank"] <= len(ranked) * 0.1]
    counts = [len(top_10_percent), (top_10_percent["neighbourhood_group"] == config.CITY).sum()]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(["All concatenated records", config.CITY], counts, color=["#4C72B0", "#DD8452"])
    ax.bar_label(bars, padding=3)
    ax.set_ylabel("Number of records")
    ax.set_title("Top 10% Most-Reviewed Records")
    ax.set_ylim(0, max(max(counts) * 1.12, 1))
    fig.tight_layout()
    fig.savefig(config.D3_OUTPUT_DIR / "top_10_percent_reviews_concatenated.png", dpi=150)
    plt.close(fig)


def main():
    df = pd.read_csv(config.require(config.CHCH_CONCAT))
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")

    config.D3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    price_histogram(df)
    days_since_last_review_histogram(df)
    top_10_percent_reviews(df)
    print(f"Plots saved to: {config.D3_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
