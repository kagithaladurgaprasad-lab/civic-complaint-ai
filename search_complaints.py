from sentence_transformers import SentenceTransformer

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from vector_db import client, TEXT_COLLECTION


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# SEARCH HISTORICAL COMPLAINTS
# ============================================================

def search_complaints(
    query,
    category=None,
    top_k=5
):

    # --------------------------------------------------------
    # 1. Convert query into embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # --------------------------------------------------------
    # 2. Create category filter
    # --------------------------------------------------------

    complaint_filter = None

    if category:

        complaint_filter = Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(
                        value=category
                    )
                )
            ]
        )

    # --------------------------------------------------------
    # 3. Search Qdrant
    # --------------------------------------------------------

    results = client.query_points(

        collection_name=TEXT_COLLECTION,

        query=query_embedding,

        query_filter=complaint_filter,

        limit=top_k,

        with_payload=True

    ).points

    return results