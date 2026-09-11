import requests
import pandas as pd


URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"


# -----------------------------------------
# Categories we want
# -----------------------------------------

WHERE = """
upper(complaint_type) like '%POTHOLE%'
OR upper(complaint_type) like '%STREET%'
OR upper(complaint_type) like '%GARBAGE%'
OR upper(complaint_type) like '%LITTER%'
OR upper(complaint_type) like '%DRAIN%'
OR upper(complaint_type) like '%WATER%'
OR upper(complaint_type) like '%ROAD%'
"""


# -----------------------------------------
# Download records
# -----------------------------------------

params = {
    "$limit": 50000,
    "$where": WHERE
}


print("Downloading NYC 311 complaints...")


response = requests.get(
    URL,
    params=params,
    timeout=120
)


response.raise_for_status()


data = response.json()


print(
    f"Downloaded {len(data)} records."
)


# -----------------------------------------
# Convert to DataFrame
# -----------------------------------------

df = pd.DataFrame(data)


print(
    "Columns:"
)

print(
    df.columns.tolist()
)


# -----------------------------------------
# Save raw subset
# -----------------------------------------

output_path = (
    "datasets/nyc_311_raw.csv"
)


df.to_csv(
    output_path,
    index=False
)


print(
    f"Saved to {output_path}"
)