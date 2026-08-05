import os


# Change working directory to the location of the CSV files""
os.chdir(r"C:\Users\hle91\OneDrive - University of Canterbury\Desktop\DATA202")
print(os.getcwd())


import pandas as pd

# Files in chronological order (Oct 2025 -> Jun 2026)
files = [
    ("listings (8).csv", "Oct 2025"),
    ("listings (7).csv", "Nov 2025"),
    ("listings (6).csv", "Dec 2025"),
    ("listings (5).csv", "Jan 2026"),
    ("listings (4).csv", "Feb 2026"),
    ("listings (3).csv", "Mar 2026"),
    ("listings (2).csv", "Apr 2026"),
    ("listings (1).csv", "May 2026"),
    ("listings.csv", "Jun 2026")
]

all_data = []
for file, month in files:
    df = pd.read_csv(file)

    # Filter for Christchurch City
    df = df[df["neighbourhood_group"] == "Christchurch City"].copy()

    # Add snapshot month
    df["month_year"] = month

    all_data.append(df)

christchurch_data = pd.concat(all_data, ignore_index=True)

print(christchurch_data.shape)

# Save the combined dataset
christchurch_data.to_csv("concatenate_chch.csv", index=False)

print("concatenate_chch.csv has been created successfully.")