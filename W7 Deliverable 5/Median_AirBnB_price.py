import os
import pandas as pd

# Get the directory where this script is saved
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the relative path to the CSV file
csv_path = os.path.join(script_dir, "airbnb_with_area_codes.csv")

# Load the dataset
df_airbnb = pd.read_csv(csv_path)

# Filter for Christchurch Central (Location ID 326600)
chch_central = df_airbnb[df_airbnb["area_code"] == 326600]
median_price = chch_central["price"].median()
print(f"Median Airbnb Price in Christchurch Central: ${median_price:.2f}")