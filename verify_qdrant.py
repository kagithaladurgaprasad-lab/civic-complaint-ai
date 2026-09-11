
from vector_db import client, TEXT_COLLECTION


print("Checking Qdrant collection...")

collection_info = client.get_collection(
    TEXT_COLLECTION
)

print("\nCollection:", TEXT_COLLECTION)

print(
    "Points count:",
    collection_info.points_count
)

print(
    "Vector size:",
    collection_info.config.params.vectors.size
)

print(
    "Distance:",
    collection_info.config.params.vectors.distance
)

print("\nVerification completed.")

