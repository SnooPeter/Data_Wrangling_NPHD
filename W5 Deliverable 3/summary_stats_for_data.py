import pandas as pd

# File path
#INPUT_PATH = pd.read_csv("listings_for_W5.csv")
INPUT_PATH = r"C:\Users\acil2\Downloads\listings_for_W5.csv"
# Columns needed for the analysis
KEEP_COLS = [
    "name",
    "neighbourhood_group",
    "price",
    "number_of_reviews",
    "last_review"
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[KEEP_COLS]


def summary_statistics(df: pd.DataFrame):

    print("\n===== SUMMARY STATISTICS =====\n")

    # -----------------------------
    # Missing values
    # -----------------------------
    missing = pd.DataFrame({
        "Missing": df.isna().sum(),
        "Missing %": (df.isna().mean() * 100).round(2),
        "Non-Missing": df.notna().sum()
    })

    print("Missing Values:")
    print(missing)

    # -----------------------------
    # Numerical columns
    # -----------------------------
    numeric_cols = df.select_dtypes(include="number").columns

    print("\n===== NUMERICAL COLUMNS =====\n")

    numeric_summary = df[numeric_cols].agg(
        ["count", "min", "max", "mean", "median", "std"]
    ).T

    numeric_summary["missing"] = df[numeric_cols].isna().sum()

    print(numeric_summary)

    # -----------------------------
    # Categorical columns
    # -----------------------------
    categorical_cols = df.select_dtypes(
        include=["object", "category"]
    ).columns

    print("\n===== CATEGORICAL COLUMNS =====\n")

    for col in categorical_cols:

        print(f"\n--- {col} ---")

        print(
            f"Number of unique categories: "
            f"{df[col].nunique(dropna=True)}"
        )

        print(
            f"Missing values: "
            f"{df[col].isna().sum()}"
        )

        print("\nCategory counts:")
        print(df[col].value_counts(dropna=False).head(10))


# -----------------------------
# Run the analysis
# -----------------------------

if __name__ == "__main__":

    data = load_data(INPUT_PATH)

    summary_statistics(data)
