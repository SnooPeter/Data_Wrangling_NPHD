"""Shared paths, constants and small helpers for the NPHD pipeline.

Every script takes its file locations from here, so the folder layout is
defined in one place:

    data/raw/        downloaded files; code never edits them
    data/interim/    in-between files; one step writes them, a later step reads them
    data/processed/  final analysis-ready tables
    output/          tables and charts for people, one folder per deliverable

All paths are built from this file's location, so the code works on any
computer and from any working directory.
"""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"
ENV_FILE = PROJECT_ROOT / ".env"

# --- Raw inputs (download these into data/raw/, see README) ---
# One Inside Airbnb NZ listings.csv per month, saved as listings_YYYY-MM.csv.
AIRBNB_SNAPSHOT_PATTERN = "listings_????-??.csv"
AIRBNB_SNAPSHOT_MONTHS = [
    "2025-10", "2025-11", "2025-12", "2026-01", "2026-02",
    "2026-03", "2026-04", "2026-05", "2026-06",
]
BOND_RAW = RAW_DIR / "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"

# --- Interim files (the comment names the script that writes each one) ---
CHCH_CONCAT = INTERIM_DIR / "concatenate_chch.csv"  # W5 concatenate_chch.py
CHCH_CLEAN = INTERIM_DIR / "christchurch_listings_clean.csv"  # W6 clean_christchurch.py
BOND_TIMEFRAME = INTERIM_DIR / "bond_data_timeframe.csv"  # W6 filter_timeframe.py
BOND_CLEAN = INTERIM_DIR / "bond_data_clean.csv"  # W6 clean_bond_data.py
AIRBNB_WITH_AREA_CODES = INTERIM_DIR / "airbnb_with_area_codes.csv"  # W7 fetch_area_codes.py
SQLITE_DB = INTERIM_DIR / "christchurch_housing.db"  # W7 merge_datasets_sql.py

# --- Processed files ---
MERGED = PROCESSED_DIR / "final_airbnb_bond_merged.csv"  # W7 merge_datasets.py
MERGED_SQL = PROCESSED_DIR / "final_airbnb_bond_merged_sql.csv"  # W7 merge_datasets_sql.py

# --- Output folders ---
D3_OUTPUT_DIR = OUTPUT_DIR / "W5_Deliverable_3"
D5_OUTPUT_DIR = OUTPUT_DIR / "W7_Deliverable_5"

# --- Constants ---
CITY = "Christchurch City"
# Bond quarters that overlap the Airbnb snapshots (Oct 2025 -> Jun 2026).
BOND_QUARTERS = ["2025-10-01", "2026-01-01", "2026-04-01"]
# Bond rows that summarise all dwelling types and bedroom counts for an area.
ALL_CATEGORY = "ALL"
CHRISTCHURCH_CENTRAL_SA2 = "326600"
DAYS_PER_WEEK = 7
TOP_N = 10

# Stats NZ Datafinder: Statistical Area 2 2019 layer (matches the bond data's SA2-2019 IDs).
SA2_2019_LAYER_ID = "98970"
SA2_2019_CODE_FIELD = "SA22019_V1_00"

# English month names written out, so labels do not depend on the computer's language settings.
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def require(path):
    """Stop with a helpful message if an input file does not exist yet."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input file: {path}\n"
            "If it is a raw file, see the README for what to download into data/raw/.\n"
            "Otherwise run the earlier pipeline steps first (python src/run_pipeline.py)."
        )
    return path


def month_label(year_month):
    """'2025-10' -> 'Oct 2025' (the month_year format used throughout the pipeline)."""
    year, month = year_month.split("-")
    return f"{MONTH_NAMES[int(month) - 1]} {year}"


def quarter_key(month_year):
    """Map snapshot labels ('May 2026') to bond quarter keys ('2026-04').

    Tenancy Services labels each quarter by its first month.
    """
    parts = month_year.str.split(" ", expand=True)
    month = parts[0].map({name: number for number, name in enumerate(MONTH_NAMES, start=1)})
    quarter_start = (month - 1) // 3 * 3 + 1
    return parts[1] + "-" + quarter_start.map("{:02d}".format)


def clean_area_code(codes):
    """Normalise SA2 codes to plain text ('326600'), dropping any trailing '.0'."""
    return codes.astype("string").str.replace(r"\.0$", "", regex=True).str.strip()
