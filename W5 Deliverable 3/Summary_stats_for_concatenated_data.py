import pandas as pd

INPUT_PATH = r"C:\Users\acil2\Downloads\listings_for_W5.csv"

def load_data(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        raise

def summary_statistics(df: pd.DataFrame) -> None:
    print("=" * 10, "DATASET OVERVIEW", "=" * 10)
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}\n")

    print("=" * 10, "NUMERICAL SUMMARY", "=" * 10)
    num_cols = df.select_dtypes(include="number")
    if not num_cols.empty:
        print(num_cols.describe().T[["count", "mean", "std", "min", "max"]])
    else:
        print("No numerical columns found.")
    print("\n")

    print("=" * 10, "MISSING VALUES", "=" * 10)
    missing = pd.DataFrame({
        "Missing Count": df.isna().sum(),
        "Missing %": (df.isna().mean() * 100).round(2)
    })
    missing_only = missing[missing["Missing Count"] > 0]
    
    if not missing_only.empty:
        print(missing_only.sort_values(by="Missing Count", ascending=False))
    else:
        print("No missing values found across all columns.")
    print("\n")

    print("=" * 10, "CATEGORICAL SUMMARY", "=" * 10)
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols) > 0:
        for col in cat_cols:
            n_unique = df[col].nunique(dropna=True)
            print(f"\n--- Column: {col} (Unique values: {n_unique}) ---")
            print(df[col].value_counts(dropna=False).head(10))
    else:
        print("No categorical columns found.")

if __name__ == "__main__":
    df = load_data(INPUT_PATH)
    summary_statistics(df)