# Data Wrangling — NPHD Pipeline

DATA201–DATA422 collaborative project. This project uses New Zealand **Airbnb** data to explore the Christchurch rental market.

# Deliverables

| Deliverable | Topic | Where to find it |
|---|---|---|
| 1 | Git and GitHub setup | `others/W3 Deliverable 1/` |
| 2 | KNIME workflow on the June 2026 snapshot | `others/W4 Deliverable 2/KNIME/` |
| 3 | Combine monthly snapshots, summary statistics, plots | `src/W5_Deliverable_3/`, `output/W5_Deliverable_3/` |
| 4 | Clean the Airbnb and bond data | `src/W6_Deliverable_4/`, including `cleaning_decisions.md` |
| 5 | Area codes, merge (pandas and SQL), Q1 to Q3 | `src/W7_Deliverable_5/`, including `explanation.md`; results in `output/W7_Deliverable_5/` |
| 6 | Best practices review, sanity checks, design principles | `src/W10_Deliverable_6/` |
| 7 | Automation: new months with one command | `Makefile`, `run_pipeline.py`, section "To add a new month" below |
| 8 | Final repository | this README |

# Team

| Name | GitHub | Main presenter |
|---|---|---|
| Peter Ra | [SnooPeter](https://github.com/SnooPeter) | Deliverables 2 and 8 |
| Daniel Villena | [dvi25](https://github.com/dvi25) | Deliverables 4 and 7 |
| HyunJin Lee | [hyunjinlee0131-wq](https://github.com/hyunjinlee0131-wq) | Deliverables 1 and 6 |
| Nicholas Indrawan | [nicholasindra1](https://github.com/nicholasindra1) | Deliverables 3 and 5 |

Some commits were made with AI coding assistants (shown as `claude` in the contributor list). The AI tool used is
stated in `src/W10_Deliverable_6/design_principles.md`.

# Project Structure

```
data/                 git-ignored — each team member keeps a local copy
  raw/                downloaded files; code never edits them
  interim/            in-between files; one step writes them, a later step reads them
  processed/          final analysis-ready tables
output/               tables and charts for people, one folder per deliverable (committed, so results are visible on GitHub)
Makefile              runs only the steps whose inputs changed (`make`)
run_pipeline.py       runs every step in order, for computers without make
report.qmd            short Quarto report that reads the results in output/
src/                  code, one folder per deliverable
  config.py           every file path and constant, defined once
  W5_Deliverable_3/   combine monthly snapshots, summary statistics, plots
  W6_Deliverable_4/   clean the Airbnb and bond data
  W7_Deliverable_5/   area codes and names, merge, analysis (Q1–Q3)
  W10_Deliverable_6/  best-practices review: sanity checks, design principles, change notes
others/               Deliverables 1 and 2 (including the KNIME workflow)
requirements.txt      Python packages needed
.env.example          template for the Stats NZ API key
```

**Why `output/` is committed:** generated files are normally git-ignored, because the pipeline can rebuild them
from the raw data and the code. We keep `output/` in the repository on purpose, so tutors can see the charts and
result tables on GitHub without running the pipeline. Each run rewrites these files, so git may show them as changed
even when the results are the same. If you do not mean to commit new results, run `git restore output/`.

# How to Run

**1. Install the packages** (Python 3.10 or newer):

```bash
pip install -r requirements.txt
```

**2. Put the raw data in `data/raw/`**, using exactly these file names:

| File | Where it comes from |
|---|---|
| `listings_YYYY-MM.csv`, one per month (currently `listings_2025-10.csv` … `listings_2026-08.csv`, 11 files) | [Inside Airbnb](https://insideairbnb.com/get-the-data/) → New Zealand → the summary `listings.csv` for each month. Rename each download to `listings_YYYY-MM.csv`. The pipeline uses every file with this name pattern. |
| `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` | [Tenancy Services rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/) → detailed quarterly report |

**3. Add the Stats NZ API key** (needed whenever there are listing locations not looked up before): copy
`.env.example` to `.env` in the project root and paste your [Stats NZ Datafinder](https://datafinder.stats.govt.nz/) key.

**4. Run the whole pipeline** from the project root, with either command:

```bash
make                     # reruns only the steps whose script or inputs changed
python run_pipeline.py   # no make needed; reruns every step
```

Both rebuild `data/interim/`, `data/processed/` and `output/` from the raw files, and stop with a clear message if a
file is missing, a monthly file has different columns, or a sanity check fails. The Stats NZ lookups (area codes,
then area names such as 327000 = Christchurch Central-East) are incremental: locations already in
`data/interim/airbnb_with_area_codes.csv` are reused and only new ones are sent to the API, so the step takes seconds
when nothing is new. `python run_pipeline.py --refresh-area-codes` ignores the saved lookups and queries everything
again. `make clean` deletes the generated files (but keeps the saved lookups); `make clean-all` deletes those too.
Each script in `src/` can also be run on its own.

If Quarto is installed, the last step renders `report.html` from `report.qmd`; otherwise it is skipped.

## To add a new month

1. **Download** the New Zealand `listings.csv` for the new month from [Inside Airbnb](https://insideairbnb.com/get-the-data/).
2. **Rename** it to `listings_YYYY-MM.csv` (e.g. `listings_2026-09.csv`) and put it in `data/raw/`.
3. **Run one command:** `make` (or `python run_pipeline.py`).

The months, bond quarters, plot titles and the "latest snapshot" plots all follow the files in `data/raw/`. If the
new month's quarter is not in the bond file yet, the pipeline warns and those listings have no rent data until a newer
bond file is downloaded (keep the same file name, or update `BOND_RAW` in `src/config.py` and the `Makefile`).

## Installing make and Quarto (optional)

```bash
winget install ezwinports.make   # then open a new terminal; check with: make --version
winget install Posit.Quarto      # for report.qmd; also needs: pip install jupyter
```

On macOS, make is usually already installed. Quarto can be installed with Homebrew:

```bash
brew install --cask quarto      # for report.qmd; also needs: pip install jupyter
```

# AirBNB Data

## Dataset Source

- **Dataset:** `listings.csv`
- **Country:** New Zealand
- **Snapshots:** one per month, from October 2025
- **Source:** [Inside Airbnb – Get the Data](https://insideairbnb.com/get-the-data/)

Inside Airbnb is an independent, non-commercial project that provides publicly available Airbnb listing data for research and analysis. The data is collected from publicly accessible information on the Airbnb website and is intended to help researchers, policymakers, and the public better understand the short-term rental market.

Because of its large file size, the dataset is stored locally on each team member's computer rather than in this GitHub repository.

## Dataset Columns

| Column | Description |
|---|---|
| `id` | Airbnb's unique identifier for the listing. |
| `name` | Name of the listing. |
| `host_id` | Airbnb's unique identifier for the host. |
| `host_name` | Name of the host, usually only the first name. |
| `neighbourhood_group` | The neighbourhood group determined by geocoding the listing's latitude and longitude against publicly available neighbourhood boundary data. |
| `neighbourhood` | Name of the neighbourhood where the listing is located. |
| `latitude` | Latitude (horizontal geographic coordinate) of the listing. |
| `longitude` | Longitude (vertical geographic coordinate) of the listing. |
| `room_type` | Type of accommodation offered: **Entire home/apartment** — exclusive use of the whole property; **Private room** — private bedroom, shared common areas; **Shared room** — shared sleeping space and common areas; **Hotel room** — hotel-style room offered through Airbnb. |
| `price` | Daily listing price in the local currency. The dollar sign (`$`) included in the raw export is an artifact and should be ignored. |
| `minimum_nights` | Minimum number of nights required for a booking. Calendar availability may impose different restrictions. |
| `number_of_reviews` | Total number of reviews received by the listing. |
| `last_review` | Date of the most recent review. |
| `reviews_per_month` | Average number of reviews per month over the listing's lifetime. For listings under 30 days old this equals the total review count; otherwise it's total reviews divided by the listing's age in months. |
| `calculated_host_listings_count` | Number of active listings the host has within the city/region covered by the current dataset. |
| `availability_365` | Number of days the listing is available for booking over the next 365 days. Unavailable days may be booked by guests or blocked by the host. |
| `number_of_reviews_ltm` | Number of reviews received in the last 12 months. |
| `license` | Licence, permit, or registration number for the listing, where applicable. |


# Tenancy Services Bond Dataset

## Source

Dataset: **Detailed quarterly report, January 2020 to April 2026**

Source: [Tenancy Services - Rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/)

The data comes from the Tenancy Services bond database and covers private-sector
tenancies. It is based on tenancy start date and uses Statistics New Zealand's
SA2-2019 geographic areas.

The data is not a list of rental advertisements. It summarises bonds recorded by
Tenancy Services and includes weekly rent measures.

## Column meanings

| Column | Meaning |
|---|---|
| `TimeFrame` | Start date of the quarter being reported. |
| `Location Id` | Identifier for the geographic area, based on SA2-2019. |
| `Dwelling Type` | Type of rental dwelling, such as House, Apartment, Flat, Room, or ALL. |
| `Number Of Beds` | Number of bedrooms. `ALL` combines bedroom counts and `5+` means five or more bedrooms. |
| `Total Bonds` | Total number of bonds recorded for the selected time, location, dwelling type, and bedroom group. |
| `Active Bonds` | Number of bonds that were active for the selected group. |
| `Closed Bonds` | Number of bonds that were closed for the selected group. |
| `Median Rent` | Median weekly rent for the selected group. |
| `Geometric Mean Rent` | Geometric mean of weekly rent. Tenancy Services provides this as an alternative rent measure because rents are commonly clustered at round numbers. |
| `Upper Quartile Rent` | Upper quartile estimate of weekly rent, approximately the 75th percentile. |
| `Lower Quartile Rent` | Lower quartile estimate of weekly rent, approximately the 25th percentile. |
| `Log Std Dev Weekly Rent` | Standard deviation of the natural logarithm of weekly rent. It describes the spread of weekly rents on a log scale. |