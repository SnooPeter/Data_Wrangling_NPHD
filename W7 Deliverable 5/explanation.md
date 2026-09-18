# Christchurch Spatial-Temporal Data Integration & Merge Decisions

## Source

The input datasets are:
- `data/airbnb_with_area_codes.csv`: Cleaned Airbnb Christchurch listings enriched with spatial area codes.
- `data/bond_data_timeframe.csv`: Cleaned Tenancy Services quarterly rental bond dataset.

The final integrated dataset is saved to `data/final_airbnb_bond_merged.csv`. The integration code is in `merge_datasets.py`.

## Decisions

- **Spatial Matching (`area_code` & `Location Id`):** Matched Airbnb listings to Tenancy Services bond data using official Stats NZ Statistical Area 2 (`SA2`) codes. Used a dual-layer spatial fetch strategy (checking 2025 and 2026 boundary layers) to maximize coverage.

- **Temporal Alignment (`time_key`):** Standardized monthly Airbnb observation dates (`month_year`) into quarterly periods (`time_key`) by rounding months down to the start of their respective quarters to match government quarterly bond reporting (`TimeFrame`).

- **Bond Data Aggregation Filter:** Filtered the bond dataset strictly to aggregate totals (`Dwelling Type == 'ALL'` and `Number Of Beds == 'ALL'`) to prevent Cartesian duplication and data explosion.

- **Preserving Observational Integrity (Left Join):** Performed a Left Join treating the Airbnb dataset as the primary master table to ensure zero row loss.

- **Retaining Panel Structure:** Kept repeated listing IDs across monthly snapshots to maintain time-series history from October 2025 to June 2026.

## Consequences

- Rows before merge (Airbnb): 28,795
- Rows after merge (Final Output): 28,795
- Rows lost: 0
- Unique Airbnb listing IDs: 4,117
(This means that across your entire multi-month observation window (from October 2025 to June 2026), there were 4,117 distinct individual properties being tracked in Christchurch, which expanded out to 28,795 total rows because individual listings appeared across multiple monthly snapshots.)
- Columns before merge: 18 (Airbnb) + 12 (Bond) = 30
- Columns after merge: 29 (excluding redundant join keys)
- Missing median rent rows: 6,849 (~23.8%)

## Reason for Missing Rent Data

Roughly 23.8% of the rows in the merged dataset have missing (`NaN`) values for median rent. This occurs for two main reasons:

1. **Government Privacy Suppression:** The Ministry of Business, Innovation and Employment (MBIE) and Tenancy Services legally suppress rental data for small statistical areas (SA2 zones) or low-volume quarterly windows to prevent individual landlords or tenants from being identified.

2. **Temporal Gaps:** Certain Christchurch neighborhoods had active Airbnb listings during specific months, but zero newly lodged rental bonds were recorded or published by the government during those exact quarters. 

Rather than indicating an error in the script, these missing values reflect the real-world constraints of working with public government administrative data.