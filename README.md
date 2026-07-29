# Data_Wrangling_NHPD
Group Project for Data Wrangling

id = Airbnb's unique identifier for the listing
name = Name of the listing
host_id = Airbnb's unique identifier for the host/user
host_name = Name of the host. Usually just the first name(s)
neighbourhood_group = The neighbourhood group as geocoded using the latitude and longitude against neighborhoods as defined by open or public digital shapefiles.
neighbourhood = name of the neighbourhood area
latitude = horizontal location coordinate
longitude = vertical location coordinate
room_type = "[Entire home/apt|Private room|Shared room|Hotel]

All homes are grouped into the following three room types:

Entire place
Private room
Shared room
Entire place
Entire places are best if you're seeking a home away from home. With an entire place, you'll have the whole space to yourself. This usually includes a bedroom, a bathroom, a kitchen, and a separate, dedicated entrance. Hosts should note in the description if they'll be on the property or not (ex: ""Host occupies first floor of the home""), and provide further details on the listing.

Private rooms
Private rooms are great for when you prefer a little privacy, and still value a local connection. When you book a private room, you'll have your own private room for sleeping and may share some spaces with others. You might need to walk through indoor spaces that another host or guest may occupy to get to your room.

Shared rooms
Shared rooms are for when you don't mind sharing a space with others. When you book a shared room, you'll be sleeping in a space that is shared with others and share the entire space with other people. Shared rooms are popular among flexible travelers looking for new friends and budget-friendly stays."
price = "daily price in local currency.
NOTE: the $ sign is a technical artifact of the export, please ignore it"
minimum_nights = minimum number of night stay for the listing (calendar rules may be different)
number_of_reviews = The number of reviews the listing has
last_review = The date of the last/newest review
reviews_per_month = "The average number of reviews per month the listing has over the lifetime of the listing.

Psuedocoe/~SQL:

IF scrape_date - first_review <= 30 THEN number_of_reviews
ELSE number_of_reviews / ((scrape_date - first_review + 1) / (365/12))

"
calculated_host_listings_count = The number of listings the host has in the current scrape, in the city/region geography.
availability_365 = avaliability_x. The availability of the listing x days in the future as determined by the calendar. Note a listing may not be available because it has been booked by a guest or blocked by the host.
number_of_reviews_ltm = The number of reviews the listing has (in the last 12 months)
license = The licence/permit/registration number