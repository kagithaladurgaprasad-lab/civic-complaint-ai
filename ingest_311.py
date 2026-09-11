
import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from vector_db import (
    client,
    TEXT_COLLECTION
)


# -----------------------------
# Configuration
# -----------------------------

INPUT_FILE = "datasets/nyc_311_cleaned.csv"

BATCH_SIZE = 256


# -----------------------------
# Load embedding model
# -----------------------------

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# Load dataset
# -----------------------------

print("Loading NYC 311 cleaned dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(
    f"Loaded {len(df)} complaints."
)


# -----------------------------
# Create search text
# -----------------------------

df["search_text"] = (
    df["search_text"]
    .fillna("")
    .astype(str)
)


# -----------------------------
# Ingest in batches
# -----------------------------

total = len(df)

print(
    f"\nStarting ingestion of {total} complaints..."
)


for start in range(
    0,
    total,
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        total
    )

    batch = df.iloc[
        start:end
    ]

    texts = batch[
        "search_text"
    ].tolist()

    print(
        f"Processing {start + 1} - {end} "
        f"of {total}..."
    )


    # -------------------------
    # Create embeddings
    # -------------------------

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False
    )


    # -------------------------
    # Create Qdrant points
    # -------------------------

    points = []

    for row, embedding in zip(
        batch.itertuples(
            index=False
        ),
        embeddings
    ):

        point = PointStruct(

            id=int(row.unique_key),

            vector=embedding.tolist(),

            payload={

                "complaint_id": str(
                    row.unique_key
                ),

                "created_date": str(
                    row.created_date
                ),

                "closed_date": str(
                    row.closed_date
                ),

                "complaint_type": str(
                    row.complaint_type
                ),

                "descriptor": str(
                    row.descriptor
                ),

                "title": str(
                    row.complaint_type
                ),

                "description": str(
                    row.descriptor
                ),

                "category": str(
                    row.category
                ),

                "agency": str(
                    row.agency
                ),

                "agency_name": str(
                    row.agency_name
                ),

                "status": str(
                    row.status
                ),

                "resolution_description": str(
                    row.resolution_description
                ),

                "latitude": float(
                    row.latitude
                ),

                "longitude": float(
                    row.longitude
                ),

                "borough": str(
                    row.borough
                ),

                "city": str(
                    row.city
                ),

                "search_text": str(
                    row.search_text
                ),

                "source": "NYC 311"
            }
        )

        points.append(point)


    # -------------------------
    # Upload to Qdrant
    # -------------------------

    client.upsert(
        collection_name=TEXT_COLLECTION,
        points=points
    )


print(
    "\n================================="
)

print(
    "NYC 311 ingestion completed!"
)

print(
    f"Total complaints indexed: {total}"
)

print(
    f"Collection: {TEXT_COLLECTION}"
)

print(
    "================================="
)
