import pandas as pd

# File path
#INPUT_PATH = pd.read_csv("listings_for_W5.csv")
INPUT_PATH = r"C:\Users\acil2\Downloads\listings_for_W5.csv"

def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def summary_statistics(df):

    print("===== DATASET OVERVIEW =====")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    print("\n===== NUMERICAL SUMMARY =====")
    print(df.describe().T)

    print("\n===== MISSING VALUES =====")
    missing = pd.DataFrame({
        "Missing": df.isna().sum(),
        "Missing %": (df.isna().mean() * 100).round(2)
    })
    print(missing)

    print("\n===== CATEGORICAL VARIABLES =====")
    for col in df.select_dtypes(include="object").columns:
        print(f"\n{col}:")
        print(df[col].value_counts().head(10))


df = load_data(INPUT_PATH)
summary_statistics(df)