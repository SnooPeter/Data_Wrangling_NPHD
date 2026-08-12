from pathlib import Path
import pandas as pd

# ------------------------------------------------------------------
# PATH CONFIGURATION
# Works when running the file or sending it to an interactive terminal.
# ------------------------------------------------------------------
def find_input_path() -> Path:
    relative_csv = Path("Concatenate_Chch_Data") / "concatenate_chch.csv"
    search_roots = [Path.cwd(), Path.cwd().parent]

    script_file = globals().get("__file__")
    if script_file:
        search_roots.insert(0, Path(script_file).resolve().parent.parent)

    for root in search_roots:
        candidate = root / relative_csv
        if candidate.is_file():
            return candidate

    checked = "\n".join(str(root / relative_csv) for root in search_roots)
    raise FileNotFoundError(f"Could not find concatenate_chch.csv. Checked:\n{checked}")


def load_data(path: Path | str) -> pd.DataFrame:
    file_path = Path(path)

    # Friendly check if file doesn't exist
    if not file_path.exists():
        raise FileNotFoundError(
            f"\n\n[ERROR] File not found at:\n{file_path.resolve()}\n\n"
            "Expected the repository data file at:\n"
            f"{file_path}\n"
        )

    df = pd.read_csv(file_path)

    # Parse date columns if present
    if "last_review" in df.columns:
        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")

    return df


def summary_statistics(df: pd.DataFrame) -> None:
    print("=" * 15, "DATASET OVERVIEW", "=" * 15)
    print(f"Total Rows: {df.shape[0]:,}")
    print(f"Total Columns: {df.shape[1]:,}")
    if "id" in df.columns:
        print(f"Unique Listings (id): {df['id'].nunique():,}")
    if "host_id" in df.columns:
        print(f"Unique Hosts (host_id): {df['host_id'].nunique():,}\n")

    print("=" * 15, "MISSING VALUES (PER COLUMN)", "=" * 15)
    missing = pd.DataFrame(
        {
            "Missing Count": df.isna().sum(),
            "Missing %": (df.isna().mean() * 100).round(2),
        }
    )
    print(missing.sort_values(by="Missing Count", ascending=False))
    print("\n")

    print("=" * 15, "NUMERICAL VARIABLES SUMMARY", "=" * 15)
    # Exclude non-meaningful ID columns from continuous numerical summaries
    id_cols = {"id", "host_id", "license"}
    num_cols = [
        c
        for c in df.select_dtypes(include="number").columns
        if c not in id_cols
    ]

    if num_cols:
        num_summary = df[num_cols].describe().T[
            ["count", "mean", "std", "min", "50%", "max"]
        ]
        num_summary.rename(columns={"50%": "median"}, inplace=True)
        print(num_summary.round(2))
    else:
        print("No numerical columns to summarize.")
    print("\n")

    print("=" * 15, "DATE / TIME VARIABLES SUMMARY", "=" * 15)
    date_cols = df.select_dtypes(include=["datetime64", "datetime"]).columns
    if len(date_cols) > 0:
        for col in date_cols:
            print(
                f"{col}: Min = {df[col].min().strftime('%Y-%m-%d')}, Max = {df[col].max().strftime('%Y-%m-%d')}"
            )
    else:
        print("No datetime columns found.")
    print("\n")

    print("=" * 15, "CATEGORICAL VARIABLES SUMMARY", "=" * 15)
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    cat_cols = [c for c in cat_cols if c not in ["name"]]

    for col in cat_cols:
        print(f"\n--- {col.upper()} (Unique Values: {df[col].nunique()}) ---")
        print(df[col].value_counts(dropna=False).head(10))


if __name__ == "__main__":
    input_path = find_input_path()
    df = load_data(input_path)
    summary_statistics(df)


# ------------------------------------------------------------------
# REPRODUCE KNIME PLOTS USING concatenate_chch.csv
# ------------------------------------------------------------------
def create_knime_plots(df: pd.DataFrame, output_dir: Path | str) -> None:
    import matplotlib.pyplot as plt

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Price histogram for the filtered Christchurch data.
    priced = df.dropna(subset=["price"]).copy()
    priced = priced[priced["price"] <= 2000]

    fig, ax = plt.subplots(figsize=(9, 5))
    bins = range(0, 2001, 100)
    ax.hist(
        priced["price"], bins=bins, color="#DD8452"
    )
    ax.set_xlabel("Price ($NZD)")
    ax.set_ylabel("Number of records")
    ax.set_title("Price Distribution — Christchurch City")
    fig.tight_layout()
    fig.savefig(output_dir / "price_histogram_concatenated.png", dpi=150)
    plt.show()
    plt.close(fig)

    # 2. Days since last review, using the KNIME snapshot reference date.
    reviewed = df.dropna(subset=["last_review"]).copy()
    reference_date = pd.Timestamp("2026-06-16")
    reviewed["days_since_last_review"] = (
        reference_date - reviewed["last_review"]
    ).dt.days
    reviewed = reviewed[reviewed["days_since_last_review"].between(0, 999)]

    fig, ax = plt.subplots(figsize=(9, 5))
    review_bins = [0, 30, 60, 90, 180, 365, 999]
    ax.hist(
        reviewed["days_since_last_review"],
        bins=review_bins,
        color="#55A868",
    )
    ax.set_xticks(review_bins)
    ax.set_xlabel("Days since last review")
    ax.set_ylabel("Number of records")
    ax.set_title("Distribution of Days Since Last Review")
    fig.tight_layout()
    fig.savefig(output_dir / "days_since_last_review_concatenated.png", dpi=150)
    plt.show()
    plt.close(fig)

    # 3. Top 10% most-reviewed records and their Christchurch subset.
    ranked = df.dropna(subset=["number_of_reviews"]).copy()
    ranked["rank"] = ranked["number_of_reviews"].rank(
        method="min", ascending=False
    )
    top_10_percent = ranked[ranked["rank"] <= len(ranked) * 0.1]
    all_count = len(top_10_percent)
    christchurch_count = (
        top_10_percent["neighbourhood_group"] == "Christchurch City"
    ).sum()

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["All concatenated records", "Christchurch City"]
    counts = [all_count, christchurch_count]
    bars = ax.bar(labels, counts, color=["#4C72B0", "#DD8452"])
    ax.bar_label(bars, padding=3)
    ax.set_ylabel("Number of records")
    ax.set_title("Top 10% Most-Reviewed Records")
    ax.set_ylim(0, max(max(counts) * 1.12, 1))
    fig.tight_layout()
    fig.savefig(output_dir / "top_10_percent_reviews_concatenated.png", dpi=150)
    plt.show()
    plt.close(fig)

    print(f"\nKNIME-style plots saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    script_file = globals().get("__file__")
    base_directory = Path(script_file).resolve().parent if script_file else Path.cwd()
    create_knime_plots(df, base_directory / "Reproduce KNIME")
