"""Run the whole NPHD pipeline in order: raw data -> interim -> processed -> output.

Usage (from any folder):
    python src/run_pipeline.py
    python src/run_pipeline.py --refresh-area-codes   # also re-query the Stats NZ API

Each step is an ordinary script that can also be run on its own.
The pipeline stops at the first step that fails.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import config

SRC_DIR = Path(__file__).resolve().parent
# Steps that call the Stats NZ API: slow and need a key, so their saved output is reused.
API_STEPS = {
    "W7_Deliverable_5/fetch_area_codes.py": config.AIRBNB_WITH_AREA_CODES,
    "W7_Deliverable_5/fetch_area_names.py": config.SA2_AREA_NAMES,
}

STEPS = [
    # Deliverable 3: combine the monthly snapshots, summary statistics, plots
    "W5_Deliverable_3/concatenate_chch.py",
    "W5_Deliverable_3/concatenated_plots.py",
    "W5_Deliverable_3/reproduce_knime_plots.py",
    # Deliverable 4: clean the Airbnb and bond data
    "W6_Deliverable_4/clean_christchurch.py",
    "W6_Deliverable_4/filter_timeframe.py",
    "W6_Deliverable_4/clean_bond_data.py",
    # Deliverable 5: area codes and names, merge, checks, analysis
    *API_STEPS,
    "W7_Deliverable_5/merge_datasets.py",
    "W7_Deliverable_5/merge_datasets_sql.py",
    "W7_Deliverable_5/sanity_checks.py",
    "W7_Deliverable_5/q1_median_airbnb_price.py",
    "W7_Deliverable_5/q2_price_gap.py",
    "W7_Deliverable_5/q3_supply_comparison.py",
]


def main():
    parser = argparse.ArgumentParser(description="Run the NPHD pipeline.")
    parser.add_argument(
        "--refresh-area-codes",
        action="store_true",
        help="query the Stats NZ API again even if area codes and names are already saved",
    )
    args = parser.parse_args()

    for step in STEPS:
        saved_output = API_STEPS.get(step)
        if saved_output and saved_output.exists() and not args.refresh_area_codes:
            print(f"\n=== Skipping {step} (using saved {saved_output.name}) ===", flush=True)
            continue

        print(f"\n=== Running {step} ===", flush=True)
        result = subprocess.run([sys.executable, str(SRC_DIR / step)])
        if result.returncode != 0:
            sys.exit(f"\nPipeline stopped: {step} failed.")

    print("\nPipeline finished. Results are in output/.")


if __name__ == "__main__":
    main()
