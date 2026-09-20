from pathlib import Path
import requests
import pandas as pd
from multiprocessing import Pool

# 1. Define base directories relative to THIS script file
SCRIPT_DIR = Path(__file__).resolve().parent
# If your data is in a subfolder called "data":
DATA_DIR = SCRIPT_DIR / "data" 

# Define input/output file paths
INPUT_CSV = DATA_DIR / "concatenate_chch.csv"  # Adjust if the file is in a different location
# If the file is in the same folder as the script, use: SCRIPT_DIR / "airbnb_listings.csv"
OUTPUT_CSV = DATA_DIR / "airbnb_with_area_codes.csv"

API_KEY = "daf8275647064c4cb8a6eab06fae5b27" 
LAYER_ID = "123515"  # Stats NZ SA2 layer ID

def get_area_code(lat_lng):
    lat, lng = lat_lng
    url = f"https://api.koordinates.com/v1/layers/{LAYER_ID}/vector/coordinates/?key={API_KEY}&x={lng}&y={lat}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['properties']['code']
    except Exception:
        pass
    return None

if __name__ == '__main__':
    # Check if file exists before running
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Dataset not found at: {INPUT_CSV.resolve()}")

    df_airbnb = pd.read_csv(INPUT_CSV)
    coords = list(zip(df_airbnb['latitude'], df_airbnb['longitude']))
    
    with Pool(processes=8) as pool:
        area_codes = pool.map(get_area_code, coords)
        
    df_airbnb['area_code'] = area_codes
    
    # Ensure output directory exists
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_airbnb.to_csv(OUTPUT_CSV, index=False)