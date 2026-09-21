from pathlib import Path
import sqlite3
import pandas as pd

# --- 1. DYNAMIC PATH CONFIGURATION ---
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"

AIRBNB_CSV = DATA_DIR / "airbnb_with_area_codes.csv"
BOND_CSV = DATA_DIR / "bond_data_timeframe.csv"
DB_FILE = DATA_DIR / "christchurch_housing.db"
OUTPUT_MERGED_CSV = DATA_DIR / "final_airbnb_bond_merged_sql.csv"


def get_quarter_start(date_str):
    """Converts a monthly date string (e.g. 'Oct 2025') into a quarterly start key ('YYYY-MM')."""
    if pd.isna(date_str):
        return None
    dt = pd.to_datetime(date_str, format="%b %Y", errors="coerce")
    if pd.isna(dt):
        return None
    quarter_start_month = ((dt.month - 1) // 3) * 3 + 1
    return f"{dt.year}-{quarter_start_month:02d}"


def run_sqlite_pipeline():
    if not AIRBNB_CSV.exists():
        raise FileNotFoundError(f"Missing Airbnb CSV at: {AIRBNB_CSV.resolve()}")
    if not BOND_CSV.exists():
        raise FileNotFoundError(f"Missing Bond CSV at: {BOND_CSV.resolve()}")

    print("Step 1: Loading raw CSV files into Pandas...")
    airbnb_df = pd.read_csv(AIRBNB_CSV, dtype={"area_code": "string"})
    bond_df = pd.read_csv(BOND_CSV, dtype={"Location Id": "string"})

    # --- PRE-PROCESSING FOR SQL JOIN KEYS ---
    # Clean spatial keys
    airbnb_df["area_code"] = airbnb_df["area_code"].str.replace(r"\.0$", "", regex=True).str.strip()
    bond_df["Location Id"] = bond_df["Location Id"].str.replace(r"\.0$", "", regex=True).str.strip()

    # Generate quarterly time keys (time_key) for temporal alignment
    airbnb_df["time_key"] = airbnb_df["month_year"].apply(get_quarter_start)
    bond_df["time_key"] = pd.to_datetime(bond_df["TimeFrame"], errors="coerce").dt.strftime("%Y-%m")

    print(f"Step 2: Connecting to SQLite database at: {DB_FILE.name}...")
    conn = sqlite3.connect(DB_FILE)

    # --- STEP 3: STORE DATASETS IN SQL TABLES ---
    print("Writing 'airbnb_listings' table to SQLite...")
    airbnb_df.to_sql("airbnb_listings", conn, if_exists="replace", index=False)

    print("Writing 'tenancy_bonds' table to SQLite...")
    bond_df.to_sql("tenancy_bonds", conn, if_exists="replace", index=False)

    # --- STEP 4: EXECUTE SQL JOIN ---
    print("Step 3: Executing spatial-temporal LEFT JOIN in SQLite...")
    
    # We filter bond data to aggregate totals ('ALL'/'ALL') in the JOIN/WHERE condition 
    # to maintain 1:1 key mapping and prevent row explosion.
    sql_query = """
    SELECT 
        a.id,
        a.name,
        a.host_id,
        a.host_name,
        a.neighbourhood,
        a.latitude,
        a.longitude,
        a.room_type,
        a.price,
        a.minimum_nights,
        a.number_of_reviews,
        a.last_review,
        a.reviews_per_month,
        a.calculated_host_listings_count,
        a.availability_365,
        a.number_of_reviews_ltm,
        a.month_year,
        a.area_code,
        b.TimeFrame,
        b."Dwelling Type",
        b."Number Of Beds",
        b."Total Bonds",
        b."Active Bonds",
        b."Closed Bonds",
        b."Median Rent",
        b."Geometric Mean Rent",
        b."Upper Quartile Rent",
        b."Lower Quartile Rent",
        b."Log Std Dev Weekly Rent"
    FROM airbnb_listings a
    LEFT JOIN tenancy_bonds b
        ON a.area_code = b."Location Id"
       AND a.time_key = b.time_key
       AND b."Dwelling Type" = 'ALL'
       AND b."Number Of Beds" = 'ALL';
    """

    merged_df = pd.read_sql_query(sql_query, conn)
    conn.close()

    # --- STEP 5: SAVE OUTPUT & VERIFY ---
    merged_df.to_csv(OUTPUT_MERGED_CSV, index=False)
    print(f"\nStep 4: Successfully saved SQL merged dataset to: {OUTPUT_MERGED_CSV.name}")
    print("\n--- SQL MERGE VERIFICATION ---")
    print(f"Total Rows: {len(merged_df):,}")
    print(f"Unique Listing IDs: {merged_df['id'].nunique():,}")
    print(f"Missing Rent Rows: {merged_df['Median Rent'].isna().sum():,}")


if __name__ == "__main__":
    run_sqlite_pipeline()