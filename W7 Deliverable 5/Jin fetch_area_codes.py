import os
from pathlib import Path
import sys
from multiprocessing import Pool, cpu_count
import pandas as pd
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
# Automatically loads the API key from .env without exposing it in the repo
load_dotenv()
API_KEY = os.getenv("STATS_NZ_API_KEY")

if not API_KEY:
    print("[ERROR] STATS_NZ_API_KEY not found. Please create a .env file containing your key.")
    sys.exit(1)

# --- DYNAMIC PATHING ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

INPUT_AIRBNB = (
    PROJECT_ROOT
    / "W6 Deliverable 4"
    / "data"
    / "christchurch_listings_clean.csv"
)

OUTPUT_DIR = SCRIPT_DIR / "data"
OUTPUT_AIRBNB = OUTPUT_DIR / "airbnb_with_area_codes.csv"

# --- API CONFIGURATION FOR SA2 2019 ---
LAYER_2019 = "98970"  # Statistical Area 2 2019 layer ID
AREA_CODE_FIELD = "SA22019_V1_00"  # Property field name for 2019 layer


def query_layer(lat, lon, layer_id):
    """Helper function to query a specific layer ID for a coordinate using the loaded API key."""
    url = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"
    params = {
        "key": API_KEY,
        "layer": layer_id,
        "x": lon,  
        "y": lat
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            features = (
                data.get("vectorQuery", {})
                .get("layers", {})
                .get(str(layer_id), {})
                .get("features", [])
            )
            if features:
                props = features[0]["properties"]
                # Dynamically look for the 2019 SA2 code field name
                for key in props.keys():
                    if "SA2" in key and "2019" in key:
                        return props.get(key)
                return props.get(AREA_CODE_FIELD)
    except Exception:
        pass
    return None


def fetch_area_code(args):
    """Worker function to query a single unique latitude/longitude pair."""
    lat, lon = args
    if pd.isna(lat) or pd.isna(lon):
        return (lat, lon), None
        
    area_code = query_layer(lat, lon, LAYER_2019)
    return (lat, lon), area_code


if __name__ == "__main__":
    if not INPUT_AIRBNB.exists():
        raise FileNotFoundError(f"Input dataset not found at: {INPUT_AIRBNB.resolve()}")

    print(f"Loading dataset from: {INPUT_AIRBNB.resolve()}")
    airbnb_df = pd.read_csv(INPUT_AIRBNB)
    
    # --- PRE-FLIGHT API TEST ---
    print("\nTesting API connection with SA2 2019 layer (98970)...")
    test_code = query_layer(-43.51108, 172.62388, LAYER_2019)
    
    if not test_code:
        print(f"\n[ERROR] API test failed for layer 98970. Please check your API key in .env.")
        sys.exit(1)
        
    print(f"API connection successful! Test area code resolved as: {test_code}\n")

    # 1. Extract ONLY unique coordinate pairs
    unique_coords = airbnb_df[["latitude", "longitude"]].drop_duplicates().values.tolist()
    print(f"Total rows: {len(airbnb_df):,} | Unique coordinate locations to query: {len(unique_coords):,}")
    
    coord_lookup = {}
    num_cores = cpu_count()
    print(f"Querying Stats NZ API (SA2 2019 Layer 98970) across {num_cores} worker processes...")
    
    # 2. Query API across unique coordinates
    with Pool(processes=num_cores) as pool:
        for coord_pair, area_code in tqdm(pool.imap_unordered(fetch_area_code, unique_coords), total=len(unique_coords)):
            coord_lookup[coord_pair] = area_code
            
    # 3. Map the results back to all rows
    print("Mapping 2019 area codes back to full dataset...")
    airbnb_df["area_code"] = [
        coord_lookup.get((lat, lon)) for lat, lon in zip(airbnb_df["latitude"], airbnb_df["longitude"])
    ]
    
    # 4. Save the file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    airbnb_df.to_csv(OUTPUT_AIRBNB, index=False)
    print(f"Success! SA2 2019 updated dataset saved to: {OUTPUT_AIRBNB.resolve()}")