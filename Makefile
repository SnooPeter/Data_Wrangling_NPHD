# NPHD pipeline: raw data -> interim -> processed -> output -> report.
#
#   make          rebuild only what is out of date (same as make all)
#   make clean    delete generated files (keeps the saved Stats NZ lookups)
#   make clean-all  also delete the saved Stats NZ lookups (next run re-queries the API)
#
# Each rule says: this file is made by this script from these inputs. make compares
# file dates and reruns a step only when its script or one of its inputs is newer
# than its output. Without make, `python run_pipeline.py` runs every step instead.
# Recipes only call python, so they work in both cmd.exe and bash.

PYTHON ?= python
CONFIG := src/config.py

# --- Raw inputs ---
# Every monthly snapshot in data/raw/: dropping in a new month makes the steps below rerun.
SNAPSHOTS := $(sort $(wildcard data/raw/listings_????-??.csv))
LATEST_SNAPSHOT := $(lastword $(SNAPSHOTS))
BOND_RAW := data/raw/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv

# --- Interim and processed files (same names as in src/config.py) ---
CHCH_CONCAT := data/interim/concatenate_chch.csv
CHCH_CLEAN := data/interim/christchurch_listings_clean.csv
BOND_TIMEFRAME := data/interim/bond_data_timeframe.csv
BOND_CLEAN := data/interim/bond_data_clean.csv
AREA_CODES := data/interim/airbnb_with_area_codes.csv
AREA_NAMES := data/interim/sa2_area_names.csv
SANITY_OK := data/interim/sanity_checks.ok
MERGED := data/processed/final_airbnb_bond_merged.csv
MERGED_SQL := data/processed/final_airbnb_bond_merged_sql.csv

# --- Outputs ---
D3 := output/W5_Deliverable_3
D5 := output/W7_Deliverable_5
D3_TABLES := $(D3)/missing_values.csv $(D3)/numeric_summary.csv $(D3)/date_summary.csv \
  $(D3)/categorical_summary.csv
D3_PLOTS := $(D3)/price_histogram_concatenated.png
D3_PLOTS_EXTRA := $(D3)/days_since_last_review_concatenated.png \
  $(D3)/top_10_percent_reviews_concatenated.png
KNIME_PLOTS := $(D3)/price_histogram.png
KNIME_PLOTS_EXTRA := $(D3)/days_since_last_review_histogram.png
Q1 := $(D5)/q1_median_airbnb_price.csv
Q2 := $(D5)/location_price_gaps.csv
Q2_EXTRA := $(D5)/top_price_gaps.png
Q3 := $(D5)/airbnb_vs_longterm_supply.csv
Q3_EXTRA := $(D5)/supply_comparison_stacked.png
OUTPUTS := $(D3_TABLES) $(D3_PLOTS) $(D3_PLOTS_EXTRA) $(KNIME_PLOTS) $(KNIME_PLOTS_EXTRA) \
  $(Q1) $(Q2) $(Q2_EXTRA) $(Q3) $(Q3_EXTRA)

# The Quarto report is rendered only if Quarto is installed.
HAVE_QUARTO := $(shell $(PYTHON) -c "import shutil; print(shutil.which('quarto') or '')")
REPORT := report.html

.PHONY: all clean clean-all
all: $(OUTPUTS) $(if $(HAVE_QUARTO),$(REPORT))
ifeq ($(HAVE_QUARTO),)
$(info Quarto is not installed: skipping $(REPORT) (see README))
endif

# A script that writes several files is the rule for its first file; the other files
# depend on that one with an empty recipe, so the script runs once, not once per file.

# --- Deliverable 3: combine the monthly snapshots, summary statistics, plots ---
$(CHCH_CONCAT): src/W5_Deliverable_3/concatenate_chch.py $(CONFIG) $(SNAPSHOTS)
	$(PYTHON) $<
$(D3_TABLES): $(CHCH_CONCAT) ;

$(D3_PLOTS): src/W5_Deliverable_3/concatenated_plots.py $(CONFIG) $(CHCH_CONCAT)
	$(PYTHON) $<
$(D3_PLOTS_EXTRA): $(D3_PLOTS) ;

# Uses only the newest month, so adding an older month does not rerun it.
$(KNIME_PLOTS): src/W5_Deliverable_3/reproduce_knime_plots.py $(CONFIG) $(LATEST_SNAPSHOT)
	$(PYTHON) $<
$(KNIME_PLOTS_EXTRA): $(KNIME_PLOTS) ;

# --- Deliverable 4: clean the Airbnb and bond data ---
$(CHCH_CLEAN): src/W6_Deliverable_4/clean_christchurch.py $(CONFIG) $(CHCH_CONCAT)
	$(PYTHON) $<

# The bond quarters to keep come from the snapshot months, so a new month is an input.
$(BOND_TIMEFRAME): src/W6_Deliverable_4/filter_timeframe.py $(CONFIG) $(BOND_RAW) $(SNAPSHOTS)
	$(PYTHON) $<

$(BOND_CLEAN): src/W6_Deliverable_4/clean_bond_data.py $(CONFIG) $(BOND_TIMEFRAME)
	$(PYTHON) $<

# --- Deliverable 5: area codes and names (Stats NZ API, incremental), merge ---
$(AREA_CODES): src/W7_Deliverable_5/fetch_area_codes.py $(CONFIG) $(CHCH_CLEAN)
	$(PYTHON) $<

$(AREA_NAMES): src/W7_Deliverable_5/fetch_area_names.py $(CONFIG) $(AREA_CODES)
	$(PYTHON) $<

$(MERGED): src/W7_Deliverable_5/merge_datasets.py $(CONFIG) $(AREA_CODES) $(BOND_CLEAN)
	$(PYTHON) $<

$(MERGED_SQL): src/W7_Deliverable_5/merge_datasets_sql.py src/W7_Deliverable_5/merge_datasets.py \
  $(CONFIG) $(AREA_CODES) $(BOND_CLEAN)
	$(PYTHON) $<

# --- Deliverable 6: sanity checks. They write no data, so an empty marker file records
# that they passed; the analysis below depends on it and never runs on a failed merge.
$(SANITY_OK): src/W10_Deliverable_6/sanity_checks.py $(CONFIG) $(AREA_CODES) $(MERGED) $(MERGED_SQL) $(BOND_CLEAN)
	$(PYTHON) $<
	$(PYTHON) -c "import pathlib; pathlib.Path('$@').touch()"

# --- Deliverable 5: analysis questions ---
$(Q1): src/W7_Deliverable_5/q1_median_airbnb_price.py $(CONFIG) $(MERGED) $(SANITY_OK)
	$(PYTHON) $<

$(Q2): src/W7_Deliverable_5/q2_price_gap.py $(CONFIG) $(MERGED) $(AREA_NAMES) $(SANITY_OK)
	$(PYTHON) $<
$(Q2_EXTRA): $(Q2) ;

$(Q3): src/W7_Deliverable_5/q3_supply_comparison.py $(CONFIG) $(MERGED) $(AREA_NAMES) $(SANITY_OK)
	$(PYTHON) $<
$(Q3_EXTRA): $(Q3) ;

# --- Report: reads the saved results only ---
$(REPORT): report.qmd $(OUTPUTS)
	quarto render report.qmd

# --- Cleaning ---
# The Stats NZ lookups are kept by `make clean` because rebuilding them takes
# thousands of API requests; the next run updates them incrementally.
GENERATED := $(CHCH_CONCAT) $(CHCH_CLEAN) $(BOND_TIMEFRAME) $(BOND_CLEAN) $(SANITY_OK) \
  data/interim/christchurch_housing.db $(MERGED) $(MERGED_SQL) $(OUTPUTS) $(REPORT)
DELETE := $(PYTHON) -c "import sys, pathlib; [pathlib.Path(p).unlink(missing_ok=True) for p in sys.argv[1:]]"

clean:
	$(DELETE) $(GENERATED)

clean-all: clean
	$(DELETE) $(AREA_CODES) $(AREA_NAMES)
