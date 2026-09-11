import pandas as pd

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from vector_db import (
    client,
    create_text_collection,
    TEXT_COLLECTION
)


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Load CSV
df = pd.read_csv("data/historical_complaints.csv")


# Create searchable text
texts = (
    df["title"].fillna("")
    + ". "
    + df["description"].fillna("")
)


# Generate embeddings
embeddings = model.encode(
    texts.tolist(),
    normalize_embeddings=True
)


# Create Qdrant collection
create_text_collection(embeddings.shape[1])

# Prepare points
points = []

for index, row in df.iterrows():

    point = PointStruct(
        id=int(row["complaint_id"]),

        vector=embeddings[index].tolist(),

        payload={
            "complaint_id": int(row["complaint_id"]),
            "title": row["title"],
            "description": row["description"],
            "department": row["department"],
            "category": row["category"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"])
        }
    )

    points.append(point)


# Store in Qdrant
client.upsert(
    collection_name=TEXT_COLLECTION,
    points=points
)


print(f"Successfully stored {len(points)} complaints.")