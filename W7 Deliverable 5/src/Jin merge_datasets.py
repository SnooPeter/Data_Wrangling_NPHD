from pathlib import Path
import pandas as pd

# --- DYNAMIC PATHING ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = SCRIPT_DIR.parent / "data"

AIRBNB_FILE = DATA_DIR / "airbnb_with_area_codes.csv"
FINAL_OUTPUT = DATA_DIR / "final_airbnb_bond_merged.csv"

# Auto-locate the bond dataset (checks Week 7 first, falls back to Week 6)
BOND_FILE = DATA_DIR / "bond_data_timeframe.csv"
if not BOND_FILE.exists():
    BOND_FILE = PROJECT_ROOT / "W6 Deliverable 4" / "data" / "bond_data_timeframe.csv"


def get_quarter_start(date):
    """
    Rounds a given monthly date down to the start of its respective 3-month quarter.
    Example: 
      - Oct, Nov, Dec -> 'YYYY-10' (Q4)
      - Jan, Feb, Mar -> 'YYYY-01' (Q1)
      - Apr, May, Jun -> 'YYYY-04' (Q2)
    """
    if pd.isna(date): 
        return None
    quarter_start_month = ((date.month - 1) // 3) * 3 + 1
    return pd.Timestamp(year=date.year, month=quarter_start_month, day=1).strftime("%Y-%m")


def merge_datasets():
    if not AIRBNB_FILE.exists():
        raise FileNotFoundError(f"Missing Airbnb data at: {AIRBNB_FILE.resolve()}")
    if not BOND_FILE.exists():
        raise FileNotFoundError(f"Missing Bond data at: {BOND_FILE.resolve()}")

    print(f"Loading Airbnb data...\nLoading Bond data from: {BOND_FILE.parent.name}...")
    airbnb_df = pd.read_csv(AIRBNB_FILE, dtype={"area_code": "string"})
    bond_df = pd.read_csv(BOND_FILE, dtype={"Location Id": "string"})

    # Clean spatial keys
    airbnb_df["area_code"] = airbnb_df["area_code"].str.replace(r"\.0$", "", regex=True).str.strip()
    bond_df["Location Id"] = bond_df["Location Id"].str.replace(r"\.0$", "", regex=True).str.strip()

    # --- TEMPORAL ALIGNMENT (3-Month Quarter Mapping) ---
    # Convert Airbnb monthly dates to quarterly start keys so April, May, and June map to '2026-04'
    airbnb_date = pd.to_datetime(airbnb_df["month_year"], format="%b %Y", errors="coerce")
    airbnb_df["time_key"] = airbnb_date.apply(get_quarter_start)
    
    bond_df["time_key"] = pd.to_datetime(bond_df["TimeFrame"], errors="coerce").dt.strftime("%Y-%m")

    # PREVENT DUPLICATION: Isolate total median rent for the area
    bond_totals_df = bond_df[(bond_df['Dwelling Type'] == 'ALL') & (bond_df['Number Of Beds'] == 'ALL')].copy()

    print("Executing Left Join on Area Code and 3-Month Quarter Key...")
    merged_df = pd.merge(
        airbnb_df,
        bond_totals_df,
        left_on=["area_code", "time_key"],
        right_on=["Location Id", "time_key"],
        how="left"
    )

    # Clean up redundant key columns
    merged_df.drop(columns=["Location Id", "time_key"], inplace=True, errors="ignore")

    # Save final dataset
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(FINAL_OUTPUT, index=False)
    print(f"Success! Final merged dataset written to: {FINAL_OUTPUT.resolve()}")
    print(f"Total records in merged dataset: {len(merged_df):,}")


if __name__ == "__main__":
    merge_datasets()

    # --- VERIFICATION STEP ---
    print("\nRunning verification on saved file...")
    df = pd.read_csv(DATA_DIR / "final_airbnb_bond_merged.csv")
    print(f"Total Rows: {len(df):,}")
    print(f"Unique Listings: {df['id'].nunique():,}")
    print(f"Missing Rent Rows: {df['Median Rent'].isna().sum():,}")