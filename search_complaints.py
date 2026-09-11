
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from complaint_embeddings import get_text_model

from vector_db import (
    client,
    TEXT_COLLECTION
)


def search_complaints(
    query,
    category=None,
    top_k=5
):

    # Use the shared SentenceTransformer model
    embedding_model = get_text_model()

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

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

    results = client.query_points(
        collection_name=TEXT_COLLECTION,
        query=query_embedding,
        query_filter=complaint_filter,
        limit=top_k,
        with_payload=True
    ).points

    return results

