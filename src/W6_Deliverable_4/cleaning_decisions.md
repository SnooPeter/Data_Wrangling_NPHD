# Christchurch Data Cleaning Decisions

## Source

The input is `data/interim/concatenate_chch.csv` (project root), created in
Deliverable 3 from Inside Airbnb Christchurch snapshots covering October 2025
to June 2026.

The cleaned file is saved to `data/interim/christchurch_listings_clean.csv`.

## Decisions

- Removed `license` because all 28,795 values were missing.
- Removed `neighbourhood_group` because every row was already Christchurch City.
- Kept latitude, longitude, price, availability, listing details, and
  `month_year` for future comparisons.
- Kept repeated listing IDs because the same listing can appear in different
  monthly snapshots.
- Kept missing values instead of filling them with estimated values.
- Converted numeric columns to numeric types and `last_review` to a date.

## Consequences

- Rows before cleaning: 28,795
- Rows after cleaning: 28,795
- Rows lost: 0
- Columns before cleaning: 19
- Columns after cleaning: 17
- Missing prices: 10,667 rows
- Missing latest review dates: 2,627 rows
- Missing minimum-night values: 37 rows

Rows with missing prices will need to be excluded from analyses that calculate
rental prices, but they remain available for other analyses.

## Bond data cleaning

The filtered bond data comes from the Tenancy Services report and is saved as
`data/interim/bond_data_timeframe.csv`. The cleaning code is in
`clean_bond_data.py`.

- Removed 94 rows with a missing `Location Id`, because they cannot be matched
  to a location.
- Kept `Location Id` and `TimeFrame` for the future comparison.
- Removed 127 rows with a `-99` ID because they aggregate rows rather than individual observations.
- Converted `TimeFrame` to a date and the rent and bond columns to numeric.
- Kept `Number Of Beds` as text because it includes values such as `ALL` and
  `5+`.

The bond data went from 27,212 rows to 26,991 rows. The cleaned file is saved as
`data/interim/bond_data_clean.csv`.
