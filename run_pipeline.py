"""Run the whole NPHD pipeline in order: raw data -> interim -> processed -> output.

Usage (from any folder):
    python run_pipeline.py
    python run_pipeline.py --refresh-area-codes   # ignore saved area codes, re-query everything

This is the Python version of the Makefile, for computers without make. It always
runs every step; `make` reruns only the steps whose inputs changed.
Each step is an ordinary script that can also be run on its own.
The pipeline stops at the first step that fails.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.append(str(SRC_DIR))  # lets this file find src/config.py
import config

REPORT = PROJECT_ROOT / "report.qmd"
# Steps that call the Stats NZ API. They always run, but reuse their saved results and
# only query locations not seen before, so they are fast when no new month was added.
API_STEPS = [
    "W7_Deliverable_5/fetch_area_codes.py",
    "W7_Deliverable_5/fetch_area_names.py",
]

STEPS = [
    # Deliverable 3: combine the monthly snapshots, summary statistics, plots
    "W5_Deliverable_3/concatenate_chch.py",
    "W5_Deliverable_3/concatenated_plots.py",
    "W5_Deliverable_3/reproduce_knime_plots.py",
    # Deliverable 4: clean the Airbnb and bond data
    "W6_Deliverable_4/clean_christchurch.py",
    "W6_Deliverable_4/filter_timeframe.py",
    "W6_Deliverable_4/clean_bond_data.py",
    # Deliverable 5: area codes and names, merge, analysis (checked by Deliverable 6)
    *API_STEPS,
    "W7_Deliverable_5/merge_datasets.py",
    "W7_Deliverable_5/merge_datasets_sql.py",
    "W10_Deliverable_6/sanity_checks.py",  # stops the pipeline if the merge looks wrong
    "W7_Deliverable_5/q1_median_airbnb_price.py",
    "W7_Deliverable_5/q2_price_gap.py",
    "W7_Deliverable_5/q3_supply_comparison.py",
]


def main():
    parser = argparse.ArgumentParser(description="Run the NPHD pipeline.")
    parser.add_argument(
        "--refresh-area-codes",
        action="store_true",
        help="ignore the saved area codes and names and query the Stats NZ API for everything",
    )
    args = parser.parse_args()

    print(f"Snapshots found: {len(config.AIRBNB_SNAPSHOT_MONTHS)} ({config.snapshot_range_label()})")
    for step in STEPS:
        command = [sys.executable, str(SRC_DIR / step)]
        if step in API_STEPS and args.refresh_area_codes:
            command.append("--refresh")

        print(f"\n=== Running {step} ===", flush=True)
        result = subprocess.run(command)
        if result.returncode != 0:
            sys.exit(f"\nPipeline stopped: {step} failed.")

    # Last step: the Quarto report, which only reads the results saved in output/.
    if shutil.which("quarto"):
        print(f"\n=== Rendering {REPORT.name} ===", flush=True)
        if subprocess.run(["quarto", "render", str(REPORT)]).returncode != 0:
            sys.exit(f"\nPipeline stopped: rendering {REPORT.name} failed.")
    else:
        print(f"\nSkipping {REPORT.name}: Quarto is not installed (see README).")

    print("\nPipeline finished. Results are in output/.")


if __name__ == "__main__":
    main()
