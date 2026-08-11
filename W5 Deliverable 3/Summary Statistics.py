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
