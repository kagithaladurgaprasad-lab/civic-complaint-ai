from sentence_transformers import SentenceTransformer

from vector_db import client, COLLECTION_NAME
from utils import calculate_distance


model = SentenceTransformer("all-MiniLM-L6-v2")


def search_nearby_complaints(
    query,
    latitude,
    longitude,
    radius_meters=100,
    top_k=10
):

    # Convert query to embedding
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # First retrieve more candidates
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        with_payload=True
    ).points

    nearby = []

    for result in results:

        complaint_lat = result.payload["latitude"]
        complaint_lon = result.payload["longitude"]

        distance = calculate_distance(
            latitude,
            longitude,
            complaint_lat,
            complaint_lon
        )

        if distance <= radius_meters:

            nearby.append({
                "complaint_id": result.payload["complaint_id"],
                "title": result.payload["title"],
                "description": result.payload["description"],
                "department": result.payload["department"],
                "category": result.payload["category"],
                "latitude": complaint_lat,
                "longitude": complaint_lon,
                "distance_meters": round(distance, 2),
                "similarity": round(result.score, 4)
            })

    return nearby