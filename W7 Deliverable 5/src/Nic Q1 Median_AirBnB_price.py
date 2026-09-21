from pathlib import Path
import pandas as pd

# Path to the directory where this script resides
SCRIPT_DIR = Path(__file__).resolve().parent

# Path to the data folder (one level up if script is in scripts/, or same level)
# If script and data folder are both in the project root:
DATA_DIR = SCRIPT_DIR.parent / "data"

# File path
file_path = DATA_DIR / "airbnb_with_area_codes.csv"

# Load dataset
df_airbnb = pd.read_csv(file_path)

# Calculate median
chch_central = df_airbnb[df_airbnb["area_code"] == 326600]
median_price = chch_central["price"].median()

print(f"Median Airbnb Price in Christchurch Central: ${median_price:.2f}")