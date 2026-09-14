# Data Wrangling — NPHD Pipeline

DATA201–DATA422 collaborative project. This project uses New Zealand **Airbnb** data to explore the Christchurch rental market.

# AirBNB Data

## Dataset Source

- **Dataset:** `listings.csv`
- **Country:** New Zealand
- **Snapshot:** June 2026
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