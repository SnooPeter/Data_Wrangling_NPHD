# Christchurch Spatial-Temporal Data Integration & Merge Decisions

## Source

The input datasets are:
- `data/airbnb_with_area_codes.csv`: Cleaned Airbnb Christchurch listings enriched with spatial area codes.
- `data/bond_data_timeframe.csv`: Cleaned Tenancy Services quarterly rental bond dataset.

- **Spatial Boundaries:** Stats NZ Statistical Area 2 2019 Generalised Layer (Layer ID `98970`).

The final integrated dataset is saved to `data/final_airbnb_bond_merged.csv`. The integration code is in `merge_datasets.py`.

## Decisions

- **Spatial Enrichment (SA2 2019):** Queried the Stats NZ Koordinates API using unique listing coordinate pairs against the **Statistical Area 2 2019** boundary layer (`98970`) to extract official `area_code` values (`SA22019_V1_00`). This ensures historical vintage compatibility with the Tenancy Services bond dataset.

- **Temporal Alignment (3-Month Quarters):** Converted monthly Airbnb snapshot dates (`month_year`) into 3-month quarterly start keys (`time_key`) using a rolling floor function. This correctly maps April, May, and June listings into Q2 (`YYYY-04`) to align with government quarterly bond reporting (`TimeFrame`).

- **Bond Data Aggregation Filter:** Filtered the bond dataset strictly to aggregate totals (`Dwelling Type == 'ALL'` and `Number Of Beds == 'ALL'`) to prevent Cartesian duplication and row explosion during the merge.

- **Observational Integrity (Left Join):** Performed a Left Join (`how="left"`) using the Airbnb dataset as the master table, ensuring zero row loss of primary listings.

- **Panel Structure:** Retained repeated listing IDs across monthly snapshots to maintain time-series continuity from October 2025 through June 2026.

## Consequences

- **Total Rows (Airbnb Master):** 28,795
- **Total Rows (Final Merged Output):** 28,795
- **Rows Lost:** 0
- **Unique Airbnb Listing IDs:** 4,117
(This means that across your entire multi-month observation window (from October 2025 to June 2026), there were 
distinct individual properties being tracked in Christchurch, which expanded out to 28,795 total rows because individual listings appeared across multiple monthly snapshots.)
- **Missing Median Rent Rows:** 4,244 (~14.7%)

## Reason for Missing Rent Data

Roughly 14.7% of the rows in the merged dataset have missing (`NaN`) values for median rent.
This is primarily due to Tenancy Services' privacy suppression policy: results are withheld
whenever a given location/quarter selection has fewer than 5 recorded bonds. The true count in
these cases is not disclosed — it could be anywhere from 0 to 4, not necessarily zero.

Of the 26 Christchurch area codes affected, 10 do appear in other quarters across the full
2020–2026 history (just not in our selected quarters), which strongly supports the suppression
explanation: 333500, 332900, 333100, 332200, 325500, 326200, 317200, 331500, 320000, 317100. 
The remaining 16 never appear in the dataset at all across 6 years of data — most
appear to be low-density areas (e.g. Banks Peninsula), consistent with persistent suppression,
but this has not been confirmed with full certainty for every case.