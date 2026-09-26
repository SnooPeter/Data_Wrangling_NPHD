# Design Principles — NPHD Pipeline (Christchurch Airbnb vs Long-Term Rentals)

> **AI used:** This document was drafted with **Claude (Anthropic), model Claude Opus 5.5**, running in Claude Code.
> The AI read our scripts and data files, then wrote this document. The team reviewed it against the code
> (see "Where the code and our intentions disagree" at the end).

## 1. Inputs

All inputs are downloaded by hand into `data/raw/`. The code only reads from this folder and never changes it.

| Input | File in `data/raw/` | Source |
|---|---|---|
| Inside Airbnb NZ listings, one snapshot per month, Oct 2025 – Jun 2026 | `listings_2025-10.csv` … `listings_2026-06.csv` (9 files) | [Inside Airbnb](https://insideairbnb.com/get-the-data/) |
| Tenancy Services rental bond data, quarterly, Q1 2020 – Q3 2026 | `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` | [Tenancy Services](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/) |
| Stats NZ SA2-2019 boundaries (layer `98970`) | — (online API) | Stats NZ Datafinder |
| API key `STATS_NZ_API_KEY` | `.env` at the project root (never committed; template in `.env.example`) | Each team member |

## 2. Outputs

**Data made by the pipeline** (`data/interim/`, `data/processed/`) — can be deleted and rebuilt at any time:

| File | Written by | Contents |
|---|---|---|
| `interim/concatenate_chch.csv` | `W5/concatenate_chch.py` | 9 snapshots, Christchurch only, with `month_year` (28,795 rows) |
| `interim/christchurch_listings_clean.csv` | `W6/clean_christchurch.py` | Types fixed, empty `license` and constant `neighbourhood_group` dropped |
| `interim/bond_data_timeframe.csv` | `W6/filter_timeframe.py` | Bond rows for the 3 matching quarters (2025-10, 2026-01, 2026-04) |
| `interim/bond_data_clean.csv` | `W6/clean_bond_data.py` | Missing and `-99` location IDs removed, types fixed |
| `interim/airbnb_with_area_codes.csv` | `W7/fetch_area_codes.py` | Listings + SA2-2019 `area_code` (needs the API; reused once made) |
| `processed/final_airbnb_bond_merged.csv` | `W7/merge_datasets.py` | One row per listing per month, with its area's bond figures for that quarter (28,795 × 29) |
| `processed/final_airbnb_bond_merged_sql.csv` | `W7/merge_datasets_sql.py` | The same join done in SQLite, used as a cross-check |

**Results for people** (`output/`):

| Folder | Files | Answers |
|---|---|---|
| `output/W5_Deliverable_3/` | `missing_values.csv`, `numeric_summary.csv`, `categorical_summary.csv`, `date_summary.csv` + 5 charts | Summary statistics for every column; KNIME-style plots |
| `output/W7_Deliverable_5/` | console output of `q1_median_airbnb_price.py` | Q1: median nightly Airbnb price in Christchurch Central (SA2 326600) — **$239.00** |
| | `location_price_gaps.csv`, `top_price_gaps.png` | Q2: areas with the biggest gap between the Airbnb nightly price and long-term daily rent |
| | `airbnb_vs_longterm_supply.csv`, `supply_comparison_stacked.png` | Q3: Airbnb listings vs long-term rentals per area |

## 3. Main steps

```
data/raw/listings_*.csv ─► [D3] concatenate_chch ─► interim/concatenate_chch.csv ─► summary stats, plots ─► output/W5_…
                                                            │
                                                            ▼
                                             [D4] clean_christchurch ─► interim/christchurch_listings_clean.csv
                                                                                        │
                                             [D5] fetch_area_codes (Stats NZ API) ─► interim/airbnb_with_area_codes.csv
                                                                                        │
data/raw/Detailed-Quarterly…csv ─► [D4] filter_timeframe ─► clean_bond_data ─► interim/bond_data_clean.csv
                                                                                        │
                                             [D5] merge (pandas + SQL) on (area code, quarter)
                                                                                        ▼
                                                        processed/final_airbnb_bond_merged.csv
                                                                                        │
                                             [D5] sanity_checks ─► Q1, Q2, Q3 ─► output/W7_…
```

1. **Combine (Deliverable 3)** — each monthly NZ snapshot is filtered to Christchurch City and labelled with its
   `month_year`, then all nine are stacked. Summary statistics cover every column: count/mean/std/min/median/max for
   numeric columns, categories and counts for text columns, date range, and missing values per column.
2. **Clean (Deliverable 4)** — convert types, drop columns that carry no information, and keep repeated listing IDs
   because each month's snapshot matters. Missing values are kept, not invented. The bond data is cut to the three
   quarters that overlap the listings, and rows without a usable location are removed.
3. **Spatial enrichment** — each *unique* latitude/longitude pair is sent to the Stats NZ API to get its SA2-2019 code.
   SA2-**2019** is used because the bond data uses 2019 boundaries.
4. **Temporal alignment** — monthly labels (`"May 2026"`) are mapped to the first month of their quarter (`"2026-04"`),
   which is how Tenancy Services labels `TimeFrame`.
5. **Merge** — a left join on (area code, quarter), using only the bond rows where `Dwelling Type == ALL` and
   `Number Of Beds == ALL`, so each area/quarter matches exactly one row. Every listing-month is kept, even when the
   bond data is suppressed (fewer than 5 bonds), which leaves 4,244 rows (14.7%) without a median rent.
6. **Sanity checks** — row counts, duplicates, correct quarter, plausible rents, and pandas vs SQL agreement. The
   pipeline stops if any check fails.
7. **Analysis** — Q1: median `price` in SA2 326600. Q2: `price − Median Rent / 7` per row, then mean/median/count per
   area, ranked by median. Q3: unique Airbnb listing IDs per area vs the highest `Active Bonds` per area.

## 4. Coding and software strategies

Best practices from the Week 9 lectures that the project follows:

- **Standard project layout.** `data/raw` → `data/interim` → `data/processed` → `output`, with code in `src/`.
  Raw data is read-only, and data flows one way: nothing reads from `output/`. Everything except `data/raw/` can be
  deleted and rebuilt with one command (`python src/run_pipeline.py`).
- **Single source of truth (DRY).** Every path and constant (city name, quarters, SA2 layer, the SA2 code for
  Christchurch Central, days per week) is defined once in `src/config.py`. Shared logic, such as the quarter mapping and
  the join keys, is written once and reused. The duplicate table and chart scripts were merged.
- **Reproducibility on any computer.** Paths are built from each script's own location (`Path(__file__)`), never from
  the terminal's folder or a `C:\Users\...` path. Month labels do not depend on the computer's language settings. Sorts
  are stable, so ties come out in the same order on every pandas version. `requirements.txt` lists the packages. We
  tested the pipeline on pandas 2.3 and 3.0 and got identical results.
- **Version control with Git/GitHub, but no data or secrets in the repo.** Data files, generated tables and `.env` are
  git-ignored. The API key is read with `python-dotenv` and never appears in code; `.env.example` shows teammates what
  to create.
- **Fail loudly, not silently.** A missing input stops the script with a message that says what to download or which
  step to run. API errors are reported instead of being swallowed. `validate="many_to_one"` makes the merge raise an
  error if a bond key is ever duplicated. The runner stops at the first failing step.
- **Validate results (sanity checks).** The merge is done twice (pandas and SQL) and `sanity_checks.py` compares them,
  along with row counts, duplicates, quarter alignment and rent ranges.
- **Readable, modular code.** Each script has a docstring, small functions and a `main()` behind
  `if __name__ == "__main__":`, with `snake_case` file names. The original authors are credited in the docstrings.
- **Efficiency.** The API is queried once per unique coordinate pair (not once per row) using a small thread pool, and
  its result is cached so it isn't fetched again on every run.
- **Documented decisions.** `cleaning_decisions.md` (Deliverable 4) and `explanation.md` (Deliverable 5) record what was
  done, why, and the effect on row counts.

## 5. Where the code and our intentions disagree

Checking this document against the code turned up these disconnects:

1. **Bond input was not the cleaned file** — *fixed.* We intended to merge the *cleaned* bond data (as `explanation.md`
   says), but the merge read `bond_data_timeframe.csv`. It now reads `bond_data_clean.csv`. The result is identical,
   because the removed `-99` and blank IDs never matched an area.
2. **Stale numbers in the write-ups** — *fixed.* `explanation.md` said 4,277 rows (14.9%) had no median rent; the code
   gives 4,244 (14.7%). `cleaning_decisions.md` said the bond data went to 27,118 rows; the code gives 26,991 (it also
   removes 127 `-99` rows).
3. **Q3 compares different time windows** — *kept for now, by team decision.* Airbnb supply counts unique listings over
   **9 months**, while long-term supply is the bond count for a **single quarter**. This overstates Airbnb supply
   relative to rentals (e.g. area 327000: 402 listings over 9 months vs 379 in the Apr–Jun 2026 quarter). The script's
   docstring notes this limitation.
