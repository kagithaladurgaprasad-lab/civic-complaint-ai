
import pandas as pd


# =========================================
# FILE PATHS
# =========================================

INPUT_FILE = "datasets/nyc_311_raw.csv"
OUTPUT_FILE = "datasets/nyc_311_cleaned.csv"


# =========================================
# LOAD DATA
# =========================================

print("Loading NYC 311 dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(
    f"Loaded {len(df)} records."
)


# =========================================
# CLEAN TEXT
# =========================================

df["complaint_type"] = (
    df["complaint_type"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["descriptor"] = (
    df["descriptor"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["agency_name"] = (
    df["agency_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["status"] = (
    df["status"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# =========================================
# CATEGORY MAPPING
# =========================================

def map_category(row):

    complaint_type = row["complaint_type"].upper()
    descriptor = row["descriptor"].upper()

    # -------------------------------------
    # POTHOLE
    # -------------------------------------

    if (
        "POTHOLE" in descriptor
        or "POTHOLE" in complaint_type
    ):
        return "Pothole"


    # -------------------------------------
    # STREETLIGHT
    # -------------------------------------

    if (
        "STREET LIGHT" in complaint_type
        or "STREET LIGHT" in descriptor
        or "LAMPPOST" in descriptor
        or "LUMINAIRE" in descriptor
    ):
        return "Streetlight"


    # -------------------------------------
    # GARBAGE / LITTER
    # -------------------------------------

    if (
        "LITTER" in complaint_type
        or "LITTER" in descriptor
        or "GARBAGE" in complaint_type
        or "GARBAGE" in descriptor
        or "OVERFLOWING" in descriptor
        and "BASKET" in descriptor
    ):
        return "Garbage"


    # -------------------------------------
    # DRAINAGE / WATERLOGGING
    # -------------------------------------

    if (
        "STANDING WATER" in complaint_type
        or "STANDING WATER" in descriptor
        or "DRAIN" in complaint_type
        or "DRAIN" in descriptor
    ):
        return "Drainage"


    # -------------------------------------
    # WATER LEAKAGE
    # -------------------------------------

    if (
        "WATER LEAK" in complaint_type
        or "WATER SYSTEM" in complaint_type
        or "LEAK" in descriptor
        or "WATER MAIN" in descriptor
        or "HYDRANT LEAK" in descriptor
    ):
        return "Water Leakage"


    # -------------------------------------
    # ROAD DAMAGE
    # -------------------------------------

    if (
        "STREET CONDITION" in complaint_type
        or "ROAD" in complaint_type
        or "ROAD" in descriptor
        or "CAVE-IN" in descriptor
        or "FAILED STREET REPAIR" in descriptor
        or "ROUGH, PITTED OR CRACKED" in descriptor
    ):
        return "Road Damage"


    # -------------------------------------
    # OTHER
    # -------------------------------------

    return None


df["category"] = df.apply(
    map_category,
    axis=1
)


# =========================================
# REMOVE UNWANTED RECORDS
# =========================================

df = df[
    df["category"].notna()
].copy()


# =========================================
# REMOVE RECORDS WITHOUT LOCATION
# =========================================

df = df[
    df["latitude"].notna()
    & df["longitude"].notna()
].copy()


# =========================================
# CREATE SEARCHABLE TEXT
# =========================================

df["search_text"] = (
    "Complaint Type: "
    + df["complaint_type"]
    + "\n"
    + "Description: "
    + df["descriptor"]
    + "\n"
    + "Category: "
    + df["category"]
    + "\n"
    + "Agency: "
    + df["agency_name"]
    + "\n"
    + "Status: "
    + df["status"]
    + "\n"
    + "Resolution: "
    + df["resolution_description"].fillna("")
)


# =========================================
# SELECT USEFUL COLUMNS
# =========================================

columns = [
    "unique_key",
    "created_date",
    "closed_date",
    "complaint_type",
    "descriptor",
    "category",
    "agency",
    "agency_name",
    "status",
    "resolution_description",
    "latitude",
    "longitude",
    "borough",
    "city",
    "search_text"
]

df = df[
    columns
]


# =========================================
# SAVE CLEAN DATASET
# =========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================
# SUMMARY
# =========================================

print(
    f"\nCleaned records: {len(df)}"
)

print(
    "\nCategory distribution:"
)

print(
    df["category"]
    .value_counts()
)


print(
    f"\nSaved to: {OUTPUT_FILE}"
)

