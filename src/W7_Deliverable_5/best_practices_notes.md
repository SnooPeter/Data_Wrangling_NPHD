# Week 9 — Best Practices Review Notes

Scope: the whole Python pipeline (Deliverables 3, 4 and 5). Deliverables 1 and 2 (including the KNIME workflow) were
moved unchanged into `others/`.

## A. What we changed and why

### 1. Project layout

We reorganised the repository into the standard data-project layout:

```
data/raw/        downloaded files; code never edits them
data/interim/    in-between files; one step writes them, a later step reads them
data/processed/  final analysis-ready tables
output/          tables and charts for people, one folder per deliverable
src/             code, one folder per deliverable, plus config.py and run_pipeline.py
```

| Change | Why |
|---|---|
| Moved all code from the `W5`/`W6`/`W7 Deliverable` folders and `Concatenate_Chch_Data/` into `src/<deliverable>/`. | Code, data and results were mixed together. Keeping them apart makes clear what is source code and what can be regenerated. |
| Split data into `raw` / `interim` / `processed`. | Raw downloads can never be overwritten by accident, and everything else can be deleted and rebuilt. |
| All charts and tables go to `output/<deliverable>/`. The W5 charts used to land next to the code or in whatever folder the terminal was in. | One place for results. Data flows one way: raw → interim → processed → output. |
| Renamed the raw snapshots from `listings (1).csv` … `listings (8).csv` to `listings_2025-10.csv` … `listings_2026-06.csv`. | The old names depended on the order the browser downloaded them, so each computer could map files to the wrong month. The month is now in the file name. |
| Moved Deliverables 1 and 2 into `others/`. | They are not part of the Python pipeline. They were moved with `git mv` so the KNIME files stay tracked. |

### 2. Code

| Change | Why (best practice) |
|---|---|
| Added `src/config.py`: every path and constant (city, quarters, SA2 layer, Christchurch Central code, days per week) is defined once. | **Single source of truth / no magic numbers.** Before, each script built its own paths, and values like `326600`, `7` and `"98970"` were typed inline. |
| Added `src/run_pipeline.py`: runs all 13 steps in order, stops at the first failure, and skips the slow API step when its result already exists. | **Reproducibility:** one command rebuilds everything from raw data. |
| Added `requirements.txt` and `.env.example`. | **Reproducible environment**, so a teammate knows which packages to install and how to set up the API key. We dropped `seaborn` and `tqdm`, which were only used for one chart and a progress bar. |
| New `concatenate_chch.py` (Deliverable 3) replaces `Chch_Data_filtering.py` and `Summary Statistics.py`. It saves the summary tables as CSVs (numeric, categorical, date, missing values). | **Deliverable 3 requirements in one script.** It also avoids a version problem: `Summary Statistics.py` chose text columns by dtype `object`, which pandas 3 marks as deprecated for text columns (a warning now, and those columns will be missed in future versions). The new script classifies columns with `is_numeric_dtype`, which behaves the same on every version. |
| Merged duplicate scripts: `Nic Q2` + `price_gap_analysis.py` → `q2_price_gap.py`, and `Nic Q3` + `supply_analysis.py` → `q3_supply_comparison.py`. | **DRY.** Each pair did the same calculation and overwrote the same output file. |
| Shared helpers (quarter mapping, area-code cleaning, join inputs) are written once and reused by both merge scripts and the sanity checks. | **DRY.** `get_quarter_start()` used to be copied in two files. |
| Every script has a docstring, small functions and a `main()` behind `if __name__ == "__main__":`. Files are `snake_case`, with the original author credited in the docstring. | **Readable, modular code.** Author names in file names (`Jin merge_datasets.py`) are unnecessary because Git records who wrote what. |
| `fetch_area_codes.py`: replaced `except Exception: pass` with `requests.RequestException` handling that reports failures, and replaced the process pool with a small thread pool. | **Fail loudly.** API errors were silently turning into blank area codes. Threads suit network-bound work and avoid Windows multiprocessing problems. |
| A missing input stops the script with a message saying what to download or which step to run. `merge_datasets.py` uses `validate="many_to_one"`. | **Fail early with clear errors**, instead of a confusing `KeyError` later on. |
| Removed `plt.show()` (figures are saved and closed) and the no-op `.replace(0, pd.NA)`. | Scripts must run **unattended**, and code should not change data without a reason. |
| Month labels use a fixed English month list, and sorts use `kind="stable"`. | **Same result on every computer:** the labels do not depend on the language settings, and tied rows sort the same way on pandas 2 and 3. |
| Added `sanity_checks.py` to the pipeline (see section C). | **Validate results** before analysing them. |

### 3. Documentation

| Change | Why |
|---|---|
| `README.md`: new *Project Structure* and *How to Run* sections (install, which raw files to download and what to name them, API key, one command to run). | Someone new can reproduce the results without asking us. |
| `explanation.md`: missing-rent figure 4,277 (14.9%) → **4,244 (14.7%)**. `cleaning_decisions.md`: bond rows 27,118 → **26,991**, and it now mentions the 127 `-99` rows. | The write-ups did not match what the code actually produces. |
| `design_principles.md` (AI-assisted, Claude Opus 5.5). | Week 9 task. |

**How we checked nothing broke:** we deleted every generated file except the cached API result, ran
`python src/run_pipeline.py` from an unrelated folder, and compared every rebuilt dataset and result table with the
version from before the cleanup. All were **identical**. The only difference is the order of tied rows in the Q3
table, which is now deterministic. We ran the same test on **pandas 2.3.3 and pandas 3.0.2** and got identical results.

## B. Disconnects found between the design and the code

| # | Disconnect | Status |
|---|---|---|
| 1 | The merge read `bond_data_timeframe.csv`, but the design (and `explanation.md`) says the *cleaned* bond data is merged. | **Fixed** — it now reads `bond_data_clean.csv`. The result is identical because the removed rows never matched an area. |
| 2 | The write-ups quoted numbers the code no longer produces (4,277 missing rents; 27,118 bond rows). | **Fixed** (see A.3). |
| 3 | Q3 compares Airbnb listings counted over 9 months with long-term rentals counted for one quarter. | **Kept by team decision.** Documented in the script and in `design_principles.md`. A per-quarter comparison would change area 327000 from 402 to 379 listings, for example. |

## C. Sanity check example — the merge step

**Why this step?** The join is where rows can be silently duplicated (many-to-one keys) or silently lost (wrong keys),
and every later answer depends on it.

`src/W7_Deliverable_5/sanity_checks.py` runs automatically after the merge and stops the pipeline if any check fails:

| # | Check | Expectation | Result on our data |
|---|---|---|---|
| 1 | Rows in vs rows out | A left join must not add or lose rows | 28,795 / 28,795 ✔ |
| 2 | Duplicate (`id`, `month_year`) pairs | 0, so no listing was matched to two bond rows | 0 ✔ |
| 3 | Bond rows joined | Only `Dwelling Type = ALL`, `Number Of Beds = ALL` | True ✔ |
| 4 | Snapshot month vs bond quarter | e.g. May 2026 → quarter 2026-04 | 0 mismatches ✔ |
| 5 | Weekly Median Rent range | Believable: $100–$2,000 | $162–$1,110 ✔ |
| 6 | pandas join vs SQL join | Identical results from two independent tools | Identical ✔ |

The core of checks 1, 2 and 6:

```python
assert len(merged) == len(airbnb)                                # no rows added or lost
assert merged.duplicated(["id", "month_year"]).sum() == 0          # no row explosion
key = ["id", "month_year"]
assert merged.set_index(key)["Median Rent"].sort_index().equals(  # pandas == SQL
    merged_sql.set_index(key)["Median Rent"].sort_index()
)
```

**Manual spot check:** one Christchurch Central (SA2 326600) listing from the May 2026 snapshot was matched to
`TimeFrame = 2026-04-01` with `Median Rent = 537`. Looking up SA2 326600 / 2026-04-01 / ALL / ALL in the raw bond
file by hand gives the same row (Median Rent 537, 42 active bonds).
