from qdrant_client.models import Filter, FieldCondition, MatchValue

from vector_db import (
    client,
    IMAGE_COLLECTION
)


print("Cleaning unwanted uploaded complaint images...")


# ============================================
# DELETE RECORDS WITH UNKNOWN SOURCE
# ============================================

client.delete(
    collection_name=IMAGE_COLLECTION,

    points_selector=Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(
                    value="Unknown"
                )
            )
        ]
    )
)


print("Cleanup completed.")


# ============================================
# CHECK REMAINING POINTS
# ============================================

collection_info = client.get_collection(
    IMAGE_COLLECTION
)

print(
    "Remaining image points:",
    collection_info.points_count
)